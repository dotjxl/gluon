# Documentation index

## Steam integration, settings, and recovery

- [Native Steam Play integration](../STEAMPLAY.md) covers installation, signing, client validation, update recovery, and legacy metadata migration.
- [Runtime features and settings](../RUNTIME.md) covers game sessions, focus, overlay, per-game settings, and Cloud preparation.
- [Gluon in Steam Settings](../STEAM-SETTINGS.md) explains the switches and how Gluon identifies eligible legacy Mac games.
- [Native Steam Cloud integration](../STEAM-CLOUD.md) explains the sync boundary, recovery guards, and save preservation.
- [Launch startup and memory diagnostics](../LAUNCH-PERFORMANCE.md) covers timing, activation, cleanup, and automated evidence.

## Graphics, media, and input

- [Direct3D 9](../graphics-d3d9.md) explains the DXVK build and its render and readback probes.
- [Vulkan](../graphics-vulkan.md) explains the Wine Vulkan bridge, MoltenVK, and portability evidence.
- [OpenGL ABI](../graphics-opengl-abi.md) and [OpenGL backends](../graphics-opengl-backends.md) cover WGL aliases, context limitations, and Primordialis investigation.
- [Runtime dependencies](../graphics-runtime-dependencies.md) and [media dependencies](../graphics-runtime-media.md) cover TLS, media, and the SDL controller bus.
- [Steam overlay](../graphics-steam-overlay.md) and [complete runtime verification](../graphics-cloud-verification.md) document evidence and its limits.

## Development and project resources

- [Cloud development](../CLOUD-DEVELOPMENT.md) explains the development and build workflows.
- [Engineering notes](../NOTES.md) record older investigations and observations. Use the current guides for setup steps.
- [Support](../../SUPPORT.md) explains bug reports and log redaction.
- [License](../../LICENSE) and [third-party notices](../../NOTICE.md) identify the project's licenses and component origins.
