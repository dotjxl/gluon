# Gluon

Gluon brings Steam Play to Apple silicon Macs. Install and launch supported Windows games from your Steam library using Gluon's bundled Wine runtime.

- [Download a release](https://github.com/dotjxl/gluon/releases)
- [Read the wiki](docs/wiki/Home.md)
- [Get help or report a bug](SUPPORT.md)

## Start here

Use Steam on an Apple silicon Mac with Rosetta available. Open the Gluon `.pkg`, follow the installer prompts, then restart Steam. Install or play a Windows game from your library. For a particular game, use **Properties → Compatibility** to choose Gluon explicitly. Read the [installation and repair guide](docs/wiki/Getting-Started.md) for custom Steam locations and recovery.

While a game opens, the Steam library can show Gluon's current launch stage next to the Play controls. **Steam → Settings → Gluon** controls Windows routing for eligible legacy Mac games, Wine preload, and automatic updates. [See the settings guide](docs/STEAM-SETTINGS.md).

## Compatibility

Game compatibility varies. The runtime includes DXMT for Direct3D 10/11, DXVK for Direct3D 9, MoltenVK for Vulkan, and Wine's macOS OpenGL driver. [See graphics options and known limits](docs/wiki/Graphics-and-Compatibility.md). Use the [troubleshooting guide](docs/wiki/Troubleshooting.md) for missing windows, graphics errors, slow starts, and installer errors.

Gluon configures and locally signs a modified Steam application. It retains a verified restoration copy and uses Steam's own compatibility manager and Cloud sync. [Read how the integration and recovery work](docs/STEAMPLAY.md).

## Development and credits

Build and runtime verification run in [GitHub Actions](docs/CLOUD-DEVELOPMENT.md). [Runtime architecture](docs/RUNTIME.md) and [graphics verification](docs/graphics-cloud-verification.md) describe the test coverage. Gluon's integrated Steam Play library is derived from [NotProton](https://github.com/NotProtonNot/NotProton), with [Dobby](https://github.com/jmpews/Dobby). The pinned sources are in [the build script](steamplay/build.sh), and licenses and third-party notices are in [NOTICE.md](NOTICE.md).

Gluon is independent of Valve, CodeWeavers, and Apple.
