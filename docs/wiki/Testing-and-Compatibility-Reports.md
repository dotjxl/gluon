# Testing and compatibility reports

Game behavior depends on the Steam build, Gluon version, game version, and macOS. A report that records those inputs helps another person reproduce the result.

## Run a useful test

| Area | What to observe |
|---|---|
| Launch and stop | Install or launch from Steam, note any Gluon stage shown, reach the first usable window, then stop or exit and confirm Steam resets its state. |
| Launch time | Time from **Play** to the first usable window. Record one launch after a fresh Steam start and several repeat launches. Include whether the game's Wine prefix was already set up and whether Preload Wine was enabled. |
| Fullscreen and focus | Start in fullscreen, switch between the game and Steam, and try returning to the game from its Steam page. Note whether Steam was in Big Picture or another Space. |
| Graphics and audio | Check the main menu and actual gameplay. Record the rendering option, visible corruption, stutter, crash, or sound issue. |
| Optional Steam features | Test overlay, achievements, controller input, or Cloud when they apply. Record each observed result independently. |

Steam's Play-to-window measurement can include client work before Gluon starts. The `first visible game window after … ms` line starts at Gluon's launcher. CI uses disposable game substitutes and graphics probes for regression checks. [Launch timing and test scope](../LAUNCH-PERFORMANCE.md).

## File a report

Include the game and App ID, Gluon version, Steam build, macOS version, Mac chip, game version, and relevant settings. Describe the expected behavior, observed behavior, and smallest reproducible sequence. Attach the short redacted section of the launcher, Wine, or installer log that covers the result. A compatibility success report should say how far you played and which Steam features you observed. [Support](../../SUPPORT.md) · [Existing issues](https://github.com/dotjxl/gluon/issues).
