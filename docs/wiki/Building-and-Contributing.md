# Building and contributing

## Project layout

| Path | What it contains |
|---|---|
| `gluon/` | Installer and recovery logic, runtime selection, Steam Cloud preparation, and the CLI. |
| `tool/` and `tools/` | Shell launcher and native helpers. |
| `steamplay/` | The pinned Steam integration, build inputs, fixtures, and patch series. |
| `packaging/` | Wine runtime build, installer creation, package checks, and native probes. |
| `tests/` | Unit tests and disposable launcher and installation fixtures. |
| `docs/` | Technical documentation and the Markdown source for this Wiki. |

## Use the CLI to build and verify

Work on a branch and push it before dispatching GitHub Actions. Use the Source checks workflow for policy fixtures and pinned source checks. The Steam Play workflow covers the native integration, recovery, and package fixture. The Build workflow assembles the full macOS installer and runs runtime probes. [Cloud development instructions](../CLOUD-DEVELOPMENT.md).

```sh
REF="my-development-branch"
gh workflow run source-checks.yml --repo dotjxl/gluon --ref "$REF"
gh workflow run steamplay.yml --repo dotjxl/gluon --ref "$REF"
gh workflow run build.yml --repo dotjxl/gluon --ref "$REF" -f version=0.5-dev
```

Use the Build command for package changes; it includes native Steam Play verification. Find a run, stream its status, and download the resulting artifact through the CLI.

```sh
gh run list --repo dotjxl/gluon --branch "$REF" --workflow build.yml
```

With the run ID from that list, substitute it for `123456789` below.

```sh
gh run watch 123456789 --repo dotjxl/gluon --exit-status
gh run download 123456789 --repo dotjxl/gluon --name Gluon-0.5-dev
```

A manually dispatched build produces an Actions artifact. The project's tag-triggered build publishes a release after package verification. [Build workflow](../../.github/workflows/build.yml) · [Releases and updates](Releases-and-Updates.md).

## Maintain the Wiki through Git

The editable source is `docs/wiki/` in the project. The public Wiki has a separate Git repository.

```sh
git clone https://github.com/dotjxl/gluon.wiki.git
```

Update the source pages, then copy the changed pages to the Wiki checkout. For links between Wiki pages, use the published page name without `.md`. For links to project files, use their URL in the source branch. Keep `_Sidebar.md` in sync with the guides you publish. Review the diff and use the project's existing GitHub no-reply commit email when pushing to the public Wiki. [Project documentation index](Documentation-Index.md).
