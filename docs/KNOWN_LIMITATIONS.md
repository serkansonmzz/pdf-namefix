# Known Limitations

`pdf-namefix` is currently a local-first MVP.

## Current limitations

- Classification is filename-based only.
- PDF content is not parsed yet.
- OCR is not supported.
- AI-assisted naming is not supported in v0.1.
- Date extraction only works with common filename date formats.
- Suggested filename collisions are detected, but automatic suffix resolution is not supported yet.
- `apply` blocks when suggested filename collisions exist.
- `organize` does not rename files; it only moves or copies them into type-based folders.
- Undo is not implemented yet.
- Recursive scan can be expensive on large folders.
- Permission-denied behavior is best-effort and platform-dependent.
- Log files are written locally under `.pdf-namefix/logs/`.

## Safety guarantees

The MVP intentionally keeps these guarantees:

- no delete
- no overwrite
- preview is non-destructive
- apply asks confirmation by default
- organize asks confirmation by default
- `--yes` does not bypass safety checks
- collision situations are not silently applied
- all apply/organize executions write JSONL logs

## Recommended first-time usage

Use preview first:

```bash
uv run pdf-namefix preview ~/Downloads
```

For organize, prefer copy mode first:

```bash
uv run pdf-namefix organize ~/Downloads \
  --out ~/Documents/OrganizedPDFs \
  --copy
```
