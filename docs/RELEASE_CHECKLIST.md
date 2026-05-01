# pdf-namefix v0.1.0 Release Checklist

## Version

- [ ] `pyproject.toml` version is `0.1.0`
- [ ] `src/pdf_namefix/__init__.py` version is `0.1.0`
- [ ] `uv run pdf-namefix --version` prints `pdf-namefix 0.1.0`

## Tests

- [ ] `uv run pytest -q` passes

## CLI Smoke Test

- [ ] `uv run pdf-namefix --help` works
- [ ] `uv run pdf-namefix preview /tmp/pdf-namefix-demo` works
- [ ] `uv run pdf-namefix preview /tmp/pdf-namefix-demo --verbose` works
- [ ] `uv run pdf-namefix apply /tmp/pdf-namefix-demo --yes` works
- [ ] `uv run pdf-namefix organize /tmp/pdf-namefix-demo --out /tmp/pdf-namefix-organized --copy --yes` works

## Safety

- [ ] Preview does not rename, move, copy, or delete files
- [ ] Apply asks confirmation by default
- [ ] Apply blocks filename collisions
- [ ] Apply never overwrites existing files
- [ ] Organize asks confirmation by default
- [ ] Organize never overwrites existing files
- [ ] Organize supports `--copy`
- [ ] Logs are written under `.pdf-namefix/logs/`
- [ ] `.pdf-namefix/` is ignored by Git

## Documentation

- [ ] README has install instructions
- [ ] README has preview/apply/organize examples
- [ ] README has safe workflow guidance
- [ ] README links known limitations
- [ ] `docs/DEMO.md` exists
- [ ] `docs/FIRST_TIME_USER_GUIDE.md` exists
- [ ] `docs/KNOWN_LIMITATIONS.md` exists
- [ ] `docs/RELEASE_NOTES_v0.1.0.md` exists

## Packaging

- [ ] `uv build` succeeds
- [ ] `dist/` contains wheel and source distribution
- [ ] Local wheel install works
- [ ] `pipx install .` works
- [ ] `pdf-namefix --version` works after pipx install
- [ ] `pdf-namefix --help` works after pipx install
- [ ] README includes pipx install instructions
- [ ] `docs/INSTALL.md` exists
- [ ] `docs/PACKAGING.md` exists

## GitHub Release

- [ ] Release branch is merged into `main`
- [ ] `main` is up to date locally
- [ ] Git tag `v0.1.0` is created
- [ ] Tag is pushed to GitHub
- [ ] GitHub release `v0.1.0` is created
