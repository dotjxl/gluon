# Getting started

## Before you install

Use an Apple silicon Mac, the macOS Steam client, and Rosetta. The Gluon installer prepares Steam under your macOS account. The account needs to be able to write the chosen Steam application and its parent directory. Gluon keeps a recovery copy of the original Steam bundle. Allow space for recovery files, the runtime, and your games.

## Install and play

1. Get a `.pkg` from [Gluon Releases](https://github.com/dotjxl/gluon/releases). For a test build or a checksum, follow [releases and updates](Releases-and-Updates.md).
2. Quit Steam and any running Wine games. Open the package and follow the prompts. The installer requests administrator authorization to stage files, then configures Steam under your logged-in account.
3. Reopen Steam. Open a Windows game in the Library and choose **Install** or **Play**. To choose the tool yourself, open **Properties → Compatibility** and select Gluon where Steam offers it.
4. Open **Steam → Settings → Gluon** to review legacy Mac routing, Wine preload, and automatic updates. [Settings and launch options](Settings-and-Launch-Options.md).

The package uses ad-hoc signing for local integration. If macOS or the installer stops the installation, record the exact message. [Troubleshooting a package failure](Troubleshooting.md#the-package-fails).

## Check, repair, or remove the installation

Use `status` to see the tracked Steam build and active runtime. Close Steam and Wine before repair or uninstall.

```sh
"$HOME/Library/Application Support/Gluon/bin/gluonctl" status
"$HOME/Library/Application Support/Gluon/bin/gluonctl" repair
"$HOME/Library/Application Support/Gluon/bin/gluon-uninstall"
```

Repair normally reuses the recorded Steam copy. If you installed Steam in a custom location or have more than one copy, specify the application path.

```sh
"$HOME/Library/Application Support/Gluon/bin/gluonctl" install \
  --steam-app "$HOME/Applications/Steam.app"
```

Uninstall restores the backed-up Steam application and removes Gluon's per-user program files. It keeps game files, Wine prefixes, saves, logs, and recovery backups. [CLI reference](CLI-Reference.md) · [Installation and recovery internals](../STEAMPLAY.md#installation-and-recovery).
