# Graphics and compatibility

A game's graphics API and the backend it actually loads determine which settings apply. Use the game's own renderer information and Gluon's Wine log for evidence. [Find the relevant log](Troubleshooting.md#find-the-relevant-log).

| Game API | Bundled runtime path | What to verify |
|---|---|---|
| Direct3D 9 | DXVK through MoltenVK | Check in-game rendering. The automated Direct3D 9 probe covers a small render-and-readback case. |
| Direct3D 10/11 | DXMT through Metal | Support varies with the game and the features it uses. |
| Vulkan | Wine Vulkan loader through MoltenVK | Portability and extension support depend on the runtime and device. |
| OpenGL | Wine's macOS driver and Apple's OpenGL | Games that require features removed from Apple's core profile can still fail. |

WineD3D is a separate backend. A renderer selection in `WINE_D3D_CONFIG` applies when the game loads WineD3D. Windows kernel drivers and kernel anti-cheat are outside Gluon's compatibility path. [Per-game settings](Settings-and-Launch-Options.md#change-one-game) · [Graphics verification](../graphics-cloud-verification.md).

## Fullscreen, overlay, audio, and input

Game presentation, Steam overlay, and controller support vary by title. If a game starts with audio and the window fails to appear, try windowed mode and compare. For an overlay-specific problem, test once with `%command% GLUON_OVERLAY=0` and record the result. For a media or input problem, include the output device or controller type and the Steam Input setting in your report. [Fullscreen troubleshooting](Troubleshooting.md#steam-says-running-but-there-is-no-window) · [Overlay evidence](../graphics-steam-overlay.md) · [Media and input dependencies](../graphics-runtime-media.md).

## Title-specific behavior

| Game | Gluon behavior |
|---|---|
| Happy Wheels | Gluon selects the game's classic window to avoid the native presenter's shared-texture timeout. `%command% GLUON_HAPPY_WHEELS_CLASSIC_WINDOW=0` restores the game's default presenter. |
| Primordialis | Gluon selects the OpenGL core profile when its bundled compatibility patch is present. `%command% GLUON_GL_COMPAT_AS_CORE=0` overrides that choice. |

Report the version and settings used when confirming a game. [Testing and compatibility reports](Testing-and-Compatibility-Reports.md).

## Legacy Mac games

With **Use Gluon for 32-bit Mac games** enabled, eligible titles with a Windows launch can use their Windows build. Games marked **32-bit Mac only** need a legacy Mac runtime. For a separately installed mac32 runner, start with the check command for an installed app.

```sh
"$HOME/Library/Application Support/Gluon/bin/gluonctl" legacy-mac check "/path/to/Game.app"
```

The runner supports a subset of legacy apps. [Legacy Mac behavior and runner details](../STEAM-SETTINGS.md) · [CLI reference](CLI-Reference.md#legacy-mac-games).
