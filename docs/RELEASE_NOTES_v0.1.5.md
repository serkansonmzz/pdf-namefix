# pdf-namefix v0.1.5 Release Notes

## Status

`pdf-namefix v0.1.5` adds Markdown and JSON preview report export.

## Changes

### Markdown export

```bash
pdf-namefix preview ~/Downloads \
  --format markdown \
  --out preview-report.md
```

### JSON export

```bash
pdf-namefix preview ~/Downloads \
  --format json \
  --out preview-report.json
```

## Use cases

Markdown reports are useful for:

- Obsidian
- manual review
- sharing analysis

JSON reports are useful for:

- automation
- future AI-assisted naming
- external tools

## Safety

- export does not rename files
- export does not move files
- export does not delete files
- export uses the same preview report data
- existing report files are not overwritten by default
- use `--overwrite-report` to replace an existing report file
