# Packaging Notes

`pdf-namefix` is a Python CLI application packaged via `pyproject.toml`.

## Console script

The CLI command is exposed through:

```toml
[project.scripts]
pdf-namefix = "pdf_namefix.cli:app"
```

This is what allows users to run:

```bash
pdf-namefix preview ~/Downloads
```

after installing the package.

## Build

```bash
uv build
```

Expected output:

```text
dist/
  pdf_namefix-0.1.0.tar.gz
  pdf_namefix-0.1.0-py3-none-any.whl
```

## Local install test

```bash
python3 -m venv /tmp/pdf-namefix-install-test
source /tmp/pdf-namefix-install-test/bin/activate
pip install dist/*.whl
pdf-namefix --version
pdf-namefix --help
deactivate
```

## pipx install test

```bash
pipx install .
pdf-namefix --version
pdf-namefix --help
pipx uninstall pdf-namefix
```

## GitHub install test

```bash
pipx install "git+https://github.com/serkansonmzz/pdf-namefix.git@v0.1.0"
pdf-namefix --version
pdf-namefix --help
```

## Future PyPI publish

PyPI publishing is intentionally out of scope for v0.1.0.

Possible future flow:

```bash
uv build
uv publish
```

Publishing requires PyPI project ownership and an API token.
