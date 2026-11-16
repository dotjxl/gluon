# Troubleshooting

## A game is slow to appear

The library can show **Preparing the runtime**, **Checking game files and Steam Cloud**, **Setting up Windows files**, **Waiting for the previous session**, or **Opening the game**. The first run may create Windows files. On later runs, note the last stage you see and compare it with the launch log. Time your test from clicking **Play** to seeing the first usable game window.

## Steam says Running but there is no window

Try Steam's action button to bring the game forward. Check Mission Control if Steam and the game use different Spaces. If you hear audio and no window appears, stop the game and try its windowed mode. For Primordialis, the game’s `fullscreen` setting is in `%APPDATA%\Primordialis\settings.txt` inside its Wine prefix. Back up the file and set `fullscreen = 0` with the game closed. Other games use their own settings or documented launch arguments.

## The package fails

Look for the exact reason displayed by the installer. If it asks about Steam or Wine, quit the named application and try again. For a missing Steam application, a changed Steam bundle, or a Steam update, check `gluonctl status` and the [installation guide](Getting-Started.md#check-repair-or-remove-the-installation).

## Steam Cloud or saves are missing

Keep the game closed while investigating. Use the [Steam Cloud guide](../STEAM-CLOUD.md) to identify the active Wine prefix and any saved recovery copy before moving files. Include the exact Cloud status in a support report.

## Find the relevant log

Gluon stores logs in `~/Library/Application Support/Gluon/logs/`. An App ID is the number in the game's Steam store URL.

| Symptom | Log |
|---|---|
| Installer error | `install.log` |
| Play, Stop, or window focus | `launch-<appid>.log` |
| Graphics, sound, or game error | `wine-<appid>.log` |
| Runtime updates or repair | `agent.log` |

For a currently running game, its Wine output may still be in `wine-<appid>-session.err`. Share the short section around the issue. [See what to include in a support report](../../SUPPORT.md).
