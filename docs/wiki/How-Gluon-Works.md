# How Gluon works

## Steam compatibility and client updates

Gluon registers a compatibility tool with Steam's native manager. Steam chooses the Windows depot and supplies the game, arguments, compatibility data path, and launch verb. An explicit per-game Steam compatibility selection takes priority over Gluon's automatic policy. Legacy Gluon metadata edits are restored through the recorded migration during installation or recovery. [Steam Play integration](../STEAMPLAY.md#steam-compatibility-policy).

During Steam startup, Gluon checks the loaded client's signatures and layouts before activating its integration. The Steam build number in `gluonctl status` helps identify the tested client. A clean Steam update can be repaired while Steam and Wine are idle. The status distinguishes active client hooks from UI validation failures and staged updates. [Client validation and recovery](../STEAMPLAY.md) · [CLI reference](CLI-Reference.md).

## Game sessions and fullscreen

Steam tracks a native Gluon host, which starts the Wine session and manages Steam Stop or quit for that game. Gluon opens a named macOS app bundle so focus and window identity follow the game. For the first-window timer, the host checks for a visible game-owned window, including an elevated fullscreen window covering a display. Steam's launch message follows the current preparation stage and clears when a window appears, the session ends, or the observation times out. [Runtime features](../RUNTIME.md#game-sessions-and-responsiveness) · [Launch performance](../LAUNCH-PERFORMANCE.md).

Gluon uses Steam's supplied overlay for supported routes and passes Steam API calls through the optional bridge. Graphics and controller behavior depend on the game, graphics backend, macOS version, and Steam build. [Graphics and compatibility](Graphics-and-Compatibility.md) · [Overlay evidence](../graphics-steam-overlay.md).

## Wine runtime and save preparation

The installed runtime includes Wine, graphics translation, and supporting media and input libraries. Gluon stages runtime updates before selecting them while idle. Games using Steam AutoCloud with Windows profile paths receive a checked path view before Steam syncs. [Steam Cloud and saves](Steam-Cloud-and-Saves.md) · [Runtime components and evidence](Documentation-Index.md#graphics-media-and-input).
