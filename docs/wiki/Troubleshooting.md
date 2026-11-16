# Troubleshooting

## A game is slow to appear

| Gluon stage | What it means |
|---|---|
| Preparing the runtime | Gluon has started and is locating the configured runtime. |
| Checking game files and Steam Cloud | Gluon is validating the launch setup and any required Steam Cloud paths. |
| Setting up Windows files | Wine is creating the game's prefix. This can occur on the first launch. |
| Waiting for the previous session | Gluon is waiting for processes in this game's Wine prefix to finish. |
| Opening the game | The runtime is starting the game and its window. |

Time from clicking **Play** to the first usable window. Compare a fresh Steam start with repeat launches, and record whether the prefix already existed and whether **Preload Wine** was on. Use the launch log to identify the last stage reached. [Testing and compatibility reports](Testing-and-Compatibility-Reports.md#run-a-useful-test).

## Steam says Running but there is no window

Try the game's action button in Steam to bring it forward. Check Mission Control for a separate fullscreen Space. If you hear audio and see no window, stop the game and try its windowed mode. For Primordialis, back up `%APPDATA%\Primordialis\settings.txt` inside the active Wine prefix and set `fullscreen = 0` with the game closed. Other titles have their own display settings or documented launch arguments. [Find the active prefix](Steam-Cloud-and-Saves.md#find-the-active-prefix).

## A game fails to start or render correctly

Confirm the game has a Windows build and Gluon is the selected tool where Steam offers a choice. If Steam reports an OS error or the Play button stays disabled, record the exact message and check for a launcher log. A fresh launcher log means the launch reached Gluon. For a blank window or rendering problem, use the Wine log and test any graphics options one at a time. For missing sound or input, note the device and whether Steam's overlay or Steam Input is enabled. [Graphics and compatibility](Graphics-and-Compatibility.md).

## Steam or Gluon Settings are missing

Run `gluonctl status` and check `steamplay/steamplay.log` in the Gluon data folder. A pending state can mean Steam still needs to start so Gluon can validate the client. If the log reports incomplete hooks or a UI validation failure, include the recorded Steam build and that exact status. For an interrupted or outdated installation, quit Steam and Wine before running repair. [Installation and recovery](Getting-Started.md#check-repair-or-remove-the-installation) · [Steam compatibility and client updates](How-Gluon-Works.md#steam-compatibility-and-client-updates).

## The package fails

Copy the reason the installer displays and the relevant lines from `logs/install.log` when present. If the reason names Steam or Wine as still open, close the named application and retry. For multiple Steam copies or a custom installation path, use `install --steam-app PATH` to select the app. For a staged update, check the background agent log before retrying. [Install and repair commands](Getting-Started.md#check-repair-or-remove-the-installation) · [Releases and updates](Releases-and-Updates.md).

## Steam Cloud or saves are missing

Keep the game closed while investigating. Identify the active Wine prefix and any recovery copy before moving files. Record the exact Cloud message and the output of `cloud status APPID`. [Steam Cloud and saves](Steam-Cloud-and-Saves.md).

## Find the relevant log

Paths in this table are relative to `~/Library/Application Support/Gluon/`. An App ID is the number in the game's Steam store URL.

| Symptom | Log |
|---|---|
| Package installation fails | `logs/install.log` |
| Steam validation or Gluon settings fail | `steamplay/steamplay.log` |
| Play, Stop, window focus, or startup time | `logs/launch-<appid>.log` |
| Graphics, sound, or game error | `logs/wine-<appid>.log` |
| Cloud preparation fails | `steamplay/cloud.log` |
| Update or repair activity | `logs/agent.log` |

For a currently running game, Wine output may still be in `logs/wine-<appid>-session.err`. Share the short section around the issue. [Support and log redaction](../../SUPPORT.md).
