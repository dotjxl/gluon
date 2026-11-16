// Real preference persistence, with classification supplied by a fixture catalog.
#include "gluon_settings.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
int np_nativeplatform_is_mac32(unsigned appid) { return appid == 123; }
void np_nativeplatform_refresh(void) {}
int main(int argc, char **argv) {
    assert(argc == 2);
    if (!strcmp(argv[1], "on")) {
        assert(!gluon_settings_read_updates());
        assert(!gluon_settings_command(123, GLUON_UPDATES_ON));
        assert(gluon_settings_command(0, GLUON_UPDATES_ON) == 1);
        assert(gluon_settings_read_updates());
        assert(!gluon_settings_read_preload());
        assert(!gluon_settings_command(123, GLUON_PRELOAD_ON));
        assert(gluon_settings_command(0, GLUON_PRELOAD_ON) == 1);
        assert(gluon_settings_read_preload());
        assert(gluon_settings_mac32());
        assert(gluon_settings_auto_app(123));
        assert(!gluon_settings_command(123, GLUON_MAC32_ON));
        assert(!gluon_settings_command(0, "gluon-proton"));
        assert(gluon_settings_command(0, GLUON_MAC32_ON) == 1);
        assert(gluon_settings_mac32());
        assert(gluon_settings_auto_app(123));
        assert(!gluon_settings_auto_app(456) && !gluon_settings_auto_app(0));
    } else if (!strcmp(argv[1], "off")) {
        assert(gluon_settings_read_updates()); // Loaded by a fresh process.
        assert(gluon_settings_command(0, GLUON_UPDATES_OFF) == 1);
        assert(!gluon_settings_read_updates());
        assert(gluon_settings_read_preload());
        assert(gluon_settings_command(0, GLUON_PRELOAD_OFF) == 1);
        assert(!gluon_settings_read_preload());
        assert(gluon_settings_mac32()); // Loaded by a fresh process.
        assert(gluon_settings_auto_app(123));
        assert(gluon_settings_command(0, GLUON_MAC32_OFF) == 1);
        assert(!gluon_settings_mac32() && !gluon_settings_auto_app(123));
    } else if (!strcmp(argv[1], "read-off")) {
        assert(!gluon_settings_mac32());
        assert(!gluon_settings_read_updates());
    } else if (!strcmp(argv[1], "launch")) {
        char directory[4096], path[4096];
        assert(snprintf(directory, sizeof directory, "%s/logs", getenv("GLUON_HOME")) > 0);
        assert(!mkdir(directory, 0700));
        assert(snprintf(path, sizeof path, "%s/launch-123.log", directory) > 0);
        assert(!gluon_launch_query(123, "gluon"));
        assert(gluon_launch_query(123, "__gluon_launch_v1_bit_0") == -1);
        FILE *log = fopen(path, "w");
        assert(log);
        fprintf(log, "gluon: launch stage %d 1\ngluon: launch stage %d 5\ngluon: launch stage 22 0\n", getpid(), getpid());
        assert(!fflush(log));
        assert(gluon_launch_query(123, "__gluon_launch_v1_bit_0") == 1);
        assert(gluon_launch_query(123, "__gluon_launch_v1_bit_1") == 1);
        assert(gluon_launch_query(123, "__gluon_launch_v1_bit_2") == -1);
        assert(gluon_launch_query(123, "__gluon_launch_v1_bit_4") == 1);
        assert(gluon_launch_query(123, "__gluon_launch_v1_bit_42") == -1);
        assert(gluon_launch_query(456, "__gluon_launch_v1_bit_0") == -1);
        fprintf(log, "gluon: launch stage %d 0\n", getpid());
        assert(!fclose(log));
        assert(gluon_launch_query(123, "__gluon_launch_v1_bit_0") == -1);
    } else if (!strcmp(argv[1], "unwritable")) {
        assert(gluon_settings_command(0, GLUON_MAC32_ON) == -1);
    } else abort();
    puts("Gluon Settings preference fixture passed");
    return 0;
}
