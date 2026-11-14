/* Share the result of this client startup with Steam's web helper. */
#ifndef GLUON_CLIENT_SESSION_H
#define GLUON_CLIENT_SESSION_H
#include "util/file.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define GLUON_CLIENT_SESSION "GLUON_STEAMPLAY_SESSION"

static inline int gluon_session_path(char *path, size_t capacity) {
    const char *home = np_home_dir();
    if (!home) return 0;
    np_support_path(path, capacity, home, "client-session");
    return strlen(path) < capacity - 1;
}

static inline void gluon_session_publish(const char *state) {
    const char *token = getenv(GLUON_CLIENT_SESSION);
    char path[2048], temporary[2100];
    if (!token || !gluon_session_path(path, sizeof(path))) return;
    int size = snprintf(temporary, sizeof(temporary), "%s.XXXXXX", path);
    if (size < 0 || (size_t)size >= sizeof(temporary)) return;
    int fd = mkstemp(temporary);
    if (fd < 0) return;
    FILE *out = fdopen(fd, "w");
    if (!out) { close(fd); unlink(temporary); return; }
    int written = fprintf(out, "%ld %s %s\n", (long)getpid(), token, state);
    if (fclose(out) != 0 || written < 0 || rename(temporary, path) != 0)
        unlink(temporary);
}

static inline void gluon_session_start(void) {
    char token[32];
    unsetenv(GLUON_CLIENT_SESSION);
    snprintf(token, sizeof(token), "%08x%08x", arc4random(), arc4random());
    if (setenv(GLUON_CLIENT_SESSION, token, 1) == 0)
        gluon_session_publish("checking");
}

/* -1 is inactive or rejected, 0 is checking, 1 is ready. */
static inline int gluon_session_phase(void) {
    const char *token = getenv(GLUON_CLIENT_SESSION);
    char path[2048], seen[17], state[24];
    long pid;
    if (!token || strlen(token) != 16 || !gluon_session_path(path, sizeof(path))) return -1;
    FILE *in = fopen(path, "r");
    if (!in) return -1;
    int fields = fscanf(in, "%ld %16s %23s", &pid, seen, state);
    fclose(in);
    if (fields != 3 || pid <= 0 || strcmp(seen, token)) return -1;
    if (!strcmp(state, "ready")) return 1;
    return !strcmp(state, "checking") ? 0 : -1;
}

static inline int gluon_session_ready(void) { return gluon_session_phase() == 1; }
#endif
