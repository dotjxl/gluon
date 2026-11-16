# Releases and updates

## Choose a build

Use the [Releases page](https://github.com/dotjxl/gluon/releases) for published packages. Since the 0.5 series, stable versions use numbers such as `0.5` or `0.5.1`. A version with `-rc` is a release candidate. Development builds can also be attached to an [Actions run](https://github.com/dotjxl/gluon/actions/workflows/build.yml), where the package is inside the versioned artifact ZIP. The run shows which commit and checks produced it.

## Verify a package

Keep the `.pkg` and its matching `.pkg.sha256` in the same folder. Use the exact downloaded checksum filename. For example, for `Gluon-0.5-rc.5.pkg`, run the following from that folder.

```sh
shasum -a 256 -c Gluon-0.5-rc.5.pkg.sha256
```

An `OK` result confirms the package matches that checksum. If verification fails, download the package and checksum again from the same release or Actions run.

## Install updates

For a manual update, close Steam and Wine and open the newer verified package. Reopen Steam after setup finishes. Gluon stages versioned payloads and applies pending runtime changes while Steam and Wine are idle. [Installation and recovery](../STEAMPLAY.md#installation-and-recovery).

**Automatically update Gluon** is off by default. When enabled under **Steam → Settings → Gluon**, it checks GitHub for stable releases every six hours, verifies the package checksum, and waits until Steam and Wine have quit to apply it. Turning the setting off pauses downloads and application. Read `~/Library/Application Support/Gluon/logs/agent.log` for update activity. [Steam settings implementation](../STEAM-SETTINGS.md).

## Update or repair after a Steam client change

Run `gluonctl status` to see whether compatibility is active, staged, or failed. A clean Valve-signed Steam replacement is eligible for automatic restoration while idle. Use `repair` while Steam and Wine are closed if status reports an interrupted installation. Independently modified or ambiguous Steam bundles can require manual recovery. [How Gluon works](How-Gluon-Works.md#steam-compatibility-and-client-updates) · [Troubleshooting](Troubleshooting.md#steam-or-gluon-settings-are-missing).
