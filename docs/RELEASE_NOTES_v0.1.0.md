# pdf-namefix v0.1.0 Release Notes

## Status

`pdf-namefix v0.1.0` is the first MVP release.

This release provides a local-first CLI workflow for previewing, safely renaming, and organizing messy PDF files.

## Core Features

### Preview

```bash
uv run pdf-namefix preview ~/Downloads
```

Preview can:

- scan one or more folders
- detect PDF files
- classify PDFs using filename-based rules
- suggest cleaner filenames
- show unknown type count
- show filename collision count
- show warnings
- optionally show reasons with `--verbose`

### Apply

```bash
uv run pdf-namefix apply ~/Downloads
```

Apply can:

- safely rename PDF files
- ask confirmation by default
- skip unsafe items
- block filename collisions
- avoid overwriting existing files
- write JSONL logs under `.pdf-namefix/logs/`

### Organize

```bash
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs
```

Organize can:

- move PDFs into type-based folders
- copy PDFs with `--copy`
- ask confirmation by default
- skip existing target files
- write JSONL logs under `.pdf-namefix/logs/`

## Supported Document Types

```text
invoice
receipt
contract
report
statement
tax
offer
application
book
ebook
course
lesson
notes
paper
article
slides
manual
transcript
worksheet
guide
cheatsheet
document
unknown
```

## Safety Guarantees

This release is designed to be safe by default:

- no delete
- no overwrite
- preview-first workflow
- confirmation by default for apply/organize
- collision blocking for apply
- target-exists skip behavior
- local-only processing
- AI-free
- OCR-free

## Known Limitations

- Classification is filename-based only.
- PDF content is not parsed.
- OCR is not supported.
- AI-assisted naming is not supported.
- Undo is not implemented yet.
- Automatic collision suffixing is not implemented yet.
- Recursive scan can be expensive on large folders.

See `docs/KNOWN_LIMITATIONS.md`.

## Recommended First-Time Flow

```bash
uv run pdf-namefix preview ~/Downloads
uv run pdf-namefix apply ~/Downloads
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs --copy
```

Use `--copy` for the first organize run if you want to keep originals in place.
