// Gluon's global policy is independent of Steam's explicit per-game mappings.
#include "gluon_settings.h"
#include "nativeplatform.h"
#include "../util/file.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <spawn.h>
#include <sys/wait.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static atomic_int g_mac32 = -1;
static pthread_mutex_t g_settings_lock = PTHREAD_MUTEX_INITIALIZER;

static int preference_path(char *path, size_t cap, const char *name) {
    const char *home = np_home_dir();
    if (!home) return 0;
    np_support_path(path, cap, home, name);
    return path[0] && strlen(path) + 16 < cap;
}

bool gluon_settings_mac32(void) {
    int value = atomic_load(&g_mac32);
    if (value >= 0) return value != 0;
    pthread_mutex_lock(&g_settings_lock);
    if ((value = atomic_load(&g_mac32)) < 0) {
        value = gluon_settings_read_mac32();
        atomic_store(&g_mac32, value);
    }
    pthread_mutex_unlock(&g_settings_lock);
    return value != 0;
}

static bool read_preference(const char *name, bool fallback) {
    char path[PATH_MAX], bytes[3] = {0};
    if (!preference_path(path, sizeof path, name)) return false;
    int fd = open(path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
    if (fd < 0) return fallback && errno == ENOENT;
    struct stat info;
    ssize_t len = fstat(fd, &info) == 0 && S_ISREG(info.st_mode) && info.st_uid == getuid()
        ? read(fd, bytes, sizeof bytes) : -1;
    close(fd);
    return len == 2 && bytes[0] == '1' && bytes[1] == '\n';
}

bool gluon_settings_read_mac32(void) { return read_preference("auto-mac32", true); }
bool gluon_settings_read_preload(void) { return read_preference("preload-wine", false); }
bool gluon_settings_read_updates(void) { return read_preference("automatic-updates", false); }

static unsigned launch_stage(uint32_t appid) {
    char path[PATH_MAX], data[8193];
    const char *user = np_home_dir(), *base = getenv("GLUON_HOME");
    if (!user || !appid) return 0;
    int n = base && *base ? snprintf(path, sizeof path, "%s/logs/launch-%u.log", base, appid) :
        snprintf(path, sizeof path, "%s/Library/Application Support/Gluon/logs/launch-%u.log", user, appid);
    if (n <= 0 || (size_t)n >= sizeof path) return 0;
    int fd = open(path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
    if (fd < 0) return 0;
    struct stat info;
    off_t start = 0;
    ssize_t length = 0;
    if (!fstat(fd, &info) && S_ISREG(info.st_mode) && info.st_uid == getuid() &&
        difftime(time(NULL), info.st_mtime) <= 125.0) {
        if (info.st_size > (off_t)(sizeof data - 1)) start = info.st_size - (sizeof data - 1);
        length = pread(fd, data, sizeof data - 1, start);
    }
    close(fd);
    if (length <= 0) return 0;
    data[length] = '\0';

    static const char marker[] = "gluon: launch stage ";
    unsigned stage = 0;
    pid_t owner = 0;
    char *line = data;
    if (start) {
        line = strchr(line, '\n');
        if (!line) return 0;
        ++line;
    }
    for (char *end; (end = strchr(line, '\n')); line = end + 1) {
        *end = '\0';
        if (strncmp(line, marker, sizeof marker - 1)) continue;
        const char *pid = line + sizeof marker - 1;
        if (*pid < '1' || *pid > '9') continue;
        char *phase;
        unsigned long value = strtoul(pid, &phase, 10);
        if (value <= 1 || value > INT_MAX || phase[0] != ' ' || phase[1] < '0' ||
            phase[1] > '5' || phase[2]) continue;
        unsigned next = (unsigned)(phase[1] - '0');
        if (next == 1) owner = (pid_t)value;
        if (owner == (pid_t)value) {
            stage = next;
            if (!next) owner = 0;
        }
    }
    return stage && owner > 1 && kill(owner, 0) == 0 ? stage : 0;
}

int gluon_launch_query(uint32_t appid, const char *name) {
    static const char prefix[] = "__gluon_launch_v1_bit_";
    if (!name || strncmp(name, prefix, sizeof prefix - 1)) return 0;
    const char *bit = name + sizeof prefix - 1;
    if ((*bit != '0' && *bit != '1' && *bit != '2' && *bit != '4') || bit[1]) return -1;
    unsigned stage = launch_stage(appid);
    return (*bit == '0' ? stage != 0 : (stage & (unsigned)(*bit - '0')) != 0) ? 1 : -1;
}

// Run outside Steam's launch path. The helper uses a private prefix and exits
// within a few seconds. Give it a minimal environment without Steam or dyld.
static void *preload_worker(void *unused) {
    (void)unused;
    const char *user = np_home_dir(), *home = getenv("GLUON_HOME");
    char root[PATH_MAX], tool[PATH_MAX], user_home[PATH_MAX + 5];
    if (!user || !*user) return NULL;
    if (!home || !*home) {
        if (snprintf(root, sizeof root, "%s/Library/Application Support/Gluon", user) >= (int)sizeof root)
            return NULL;
        home = root;
    }
    if (snprintf(tool, sizeof tool, "%s/bin/gluonctl", home) >= (int)sizeof tool ||
        snprintf(user_home, sizeof user_home, "HOME=%s", user) >= (int)sizeof user_home)
        return NULL;
    char *args[] = {tool, "preload", "--home", (char *)home, NULL};
    char *env[] = {user_home, "PATH=/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE=1", NULL};
    posix_spawnattr_t attr;
    if (posix_spawnattr_init(&attr)) return NULL;
    sigset_t signals;
    sigemptyset(&signals);
    posix_spawnattr_setsigmask(&attr, &signals);
    posix_spawnattr_setflags(&attr, POSIX_SPAWN_SETSIGMASK | POSIX_SPAWN_CLOEXEC_DEFAULT);
    pid_t pid;
    int result = posix_spawn(&pid, tool, NULL, &attr, args, env);
    posix_spawnattr_destroy(&attr);
    if (!result) while (waitpid(pid, NULL, 0) < 0 && errno == EINTR) {}
    return NULL;
}

void gluon_settings_warmup(void) {
    pthread_t worker;
    if (gluon_settings_read_preload() && !pthread_create(&worker, NULL, preload_worker, NULL))
        pthread_detach(worker);
}

bool gluon_settings_mac32_effective(void) {
    return gluon_settings_mac32();
}

int gluon_settings_command(uint32_t appid, const char *name) {
    if (appid || !name) return 0;
    static const struct {
        const char *on, *off, *file;
    } preferences[] = {
        { GLUON_MAC32_ON, GLUON_MAC32_OFF, "auto-mac32" },
        { GLUON_PRELOAD_ON, GLUON_PRELOAD_OFF, "preload-wine" },
        { GLUON_UPDATES_ON, GLUON_UPDATES_OFF, "automatic-updates" },
    };
    const char *file = NULL;
    int enabled = 0, ok = 0;
    for (size_t i = 0; i < sizeof preferences / sizeof preferences[0]; ++i) {
        int on = !strcmp(name, preferences[i].on);
        if (on || !strcmp(name, preferences[i].off)) {
            file = preferences[i].file;
            enabled = on;
            break;
        }
    }
    if (!file) return 0;
    char path[PATH_MAX], temporary[PATH_MAX];
    pthread_mutex_lock(&g_settings_lock);
    if (preference_path(path, sizeof path, file)) {
        snprintf(temporary, sizeof temporary, "%s.XXXXXX", path);
        int fd = mkstemp(temporary);
        if (fd >= 0) {
            const char *value = enabled ? "1\n" : "0\n";
            int written = write(fd, value, 2) == 2 && fsync(fd) == 0;
            int closed = close(fd) == 0;
            if (written && closed && rename(temporary, path) == 0) {
                if (!strcmp(file, "auto-mac32")) atomic_store(&g_mac32, enabled);
                ok = 1;
            }
            unlink(temporary);
        }
    }
    pthread_mutex_unlock(&g_settings_lock);
    if (ok && enabled && !strcmp(file, "preload-wine")) gluon_settings_warmup();
    return ok ? 1 : -1;
}

bool gluon_settings_auto_app(uint32_t appid) {
    return appid && gluon_settings_mac32_effective() && np_nativeplatform_is_mac32(appid);
}
