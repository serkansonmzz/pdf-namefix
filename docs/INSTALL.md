# Install pdf-namefix

This guide explains how to install `pdf-namefix` as a local CLI command.

## Recommended: install with pipx from GitHub

`pipx` installs Python CLI applications in isolated environments and exposes their commands globally.

Install from the latest GitHub release tag:

```bash
pipx install "git+https://github.com/serkansonmzz/pdf-namefix.git@v0.1.0"
```

Then run:

```bash
pdf-namefix --version
pdf-namefix --help
pdf-namefix preview ~/Downloads
```

## Upgrade

```bash
pipx upgrade pdf-namefix
```

If installing from a specific Git tag, reinstall when needed:

```bash
pipx uninstall pdf-namefix
pipx install "git+https://github.com/serkansonmzz/pdf-namefix.git@v0.1.0"
```

## Uninstall

```bash
pipx uninstall pdf-namefix
```

## Development usage

For contributors:

```bash
git clone git@github.com:serkansonmzz/pdf-namefix.git
cd pdf-namefix
uv sync
uv run pdf-namefix --help
uv run pytest -q
```

## Build locally

```bash
uv build
```

This creates package artifacts under:

```text
dist/
```

Do not commit `dist/` files.
