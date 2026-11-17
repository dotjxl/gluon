# Gluon

![Gluon slogan](gluon-slogan.svg)

Gluon brings Steam Play to Apple silicon Macs. Install and launch supported Windows games from your Steam library using Gluon's bundled Wine runtime.

- [Download a release](https://github.com/dotjxl/gluon/releases)
- [Read the wiki](https://github.com/dotjxl/gluon/wiki)
- [Get help or report a bug](SUPPORT.md)

## Start here

Use Steam on an Apple silicon Mac with Rosetta available. Download the `.pkg` and its checksum from the same release or Actions run. Quit Steam and Wine, verify the download, and open the installer. If macOS offers **Open Anyway** for the verified package, look under **System Settings → Privacy & Security**. Follow the prompts, then reopen Steam. A normal installation uses the bundled runtime and needs no Terminal setup. [Installation and repair guide](docs/wiki/Getting-Started.md) · [Builds and checksum verification](docs/wiki/Releases-and-Updates.md).

Install or play a Windows game from your library. For a particular game, use **Properties → Compatibility** to choose Gluon when Steam offers it.

While a game opens, Steam can show Gluon's current launch stage in the status area to the right of **Play**. **Steam → Settings → Gluon** controls Windows routing for eligible legacy Mac games, Wine preload, and automatic updates. [See the settings guide](docs/STEAM-SETTINGS.md).

## Compatibility

Gluon is experimental. Game compatibility varies, and Steam integration requires a client that passes runtime validation. The runtime includes DXMT for Direct3D 10/11, DXVK for Direct3D 9, MoltenVK for Vulkan, and Wine's macOS OpenGL driver. [Graphics options and known limits](docs/wiki/Graphics-and-Compatibility.md) · [Troubleshooting](docs/wiki/Troubleshooting.md).

Gluon configures and locally signs a modified Steam application. It retains a verified restoration copy and uses Steam's own compatibility manager and Cloud sync. [Read how the integration and recovery work](docs/STEAMPLAY.md).

## Development and credits

Build and runtime verification run in [GitHub Actions](docs/CLOUD-DEVELOPMENT.md). [Runtime architecture](docs/RUNTIME.md) and [graphics verification](docs/graphics-cloud-verification.md) describe the test coverage. Gluon's integrated Steam Play library is derived from [NotProton](https://github.com/NotProtonNot/NotProton), with [Dobby](https://github.com/jmpews/Dobby). The pinned sources are in [the build script](steamplay/build.sh), and licenses and third-party notices are in [NOTICE.md](NOTICE.md).

Gluon is independent of Valve, CodeWeavers, and Apple.
