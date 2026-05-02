# pdf-namefix

A local-first CLI tool for previewing, safely renaming, and organizing messy PDF files.

`pdf-namefix` helps you clean up PDF-heavy folders such as `Downloads`, `Desktop`, or document archives.

It can:

- scan one or more folders for PDF files
- classify PDFs using filename-based rules
- suggest cleaner filenames
- preview all changes before touching files
- safely rename PDFs
- organize PDFs into type-based folders
- write local JSONL logs for apply/organize operations

The first version is intentionally:

- AI-free
- OCR-free
- local-only
- preview-first
- no-delete
- no-overwrite

## Why this exists

PDF folders get messy fast.

Examples:

```text
scan_239812.pdf
document-final-v3.pdf
whatsapp-document-2026.pdf
rust_lifetimes_notes.pdf
turkcell_fatura_2026-04-29.pdf
clean_architecture_book.pdf
```

`pdf-namefix` helps turn that mess into something easier to understand and organize.

Example suggested names:

```text
unknown-date_rust_lifetimes_notes.pdf
2026-04-29_turkcell_fatura_invoice.pdf
unknown-date_clean_architecture_book.pdf
```

## Current MVP Features

```text
preview  → scan PDFs, classify them, suggest names, show risks
apply    → safely rename PDFs
organize → move/copy PDFs into type-based folders
```

## Installation for Development

Clone the repository:

```bash
git clone git@github.com:serkansonmzz/pdf-namefix.git
cd pdf-namefix
```

Install dependencies:

```bash
uv sync
```

Check the CLI:

```bash
uv run pdf-namefix --help
```

## Basic Usage

### 1. Preview first

Always start with preview:

```bash
uv run pdf-namefix preview ~/Downloads
```

Scan multiple folders:

```bash
uv run pdf-namefix preview ~/Downloads ~/Desktop ~/Documents
```

Recursive scan:

```bash
uv run pdf-namefix preview ~/Downloads --recursive
```

Verbose output:

```bash
uv run pdf-namefix preview ~/Downloads --verbose
```

### 2. Apply safe renames

Preview first, then apply:

```bash
uv run pdf-namefix apply ~/Downloads
```

Skip confirmation:

```bash
uv run pdf-namefix apply ~/Downloads --yes
```

Safety behavior:

- asks confirmation by default
- blocks apply if filename collisions exist
- never overwrites existing files
- skips unsafe items
- writes a JSONL log under `.pdf-namefix/logs/`

### 3. Organize PDFs

Move PDFs into type-based folders:

```bash
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs
```

Copy PDFs instead of moving them:

```bash
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs --copy
```

Skip confirmation:

```bash
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs --copy --yes
```

Possible output structure:

```text
OrganizedPDFs/
  invoices/
  receipts/
  contracts/
  reports/
  books/
  courses/
  notes/
  papers/
  slides/
  manuals/
  unknown/
```

## Recommended Safe Workflow

For first-time usage:

```bash
uv run pdf-namefix preview ~/Downloads
uv run pdf-namefix apply ~/Downloads
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs --copy
```

Use `--copy` for the first organize run if you want to keep originals in place.

## Example Preview Output

```text
Preview mode
No files will be renamed in this command.

PDF files found: 5

1. /Users/me/Downloads/rust_lifetimes_notes.pdf (12.0 KB) [notes] confidence=0.9
   → unknown-date_rust_lifetimes_notes.pdf

2. /Users/me/Downloads/clean_architecture_book.pdf (5.1 MB) [book] confidence=0.9
   → unknown-date_clean_architecture_book.pdf

3. /Users/me/Downloads/turkcell_fatura_2026-04-29.pdf (90.0 KB) [invoice] confidence=0.9
   → 2026-04-29_turkcell_fatura_invoice.pdf

Summary
- Total PDF files: 5
- Unknown type: 1
- Suggested name collisions: 0
- Warnings: 0
```

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

The MVP is designed to be safe by default:

- preview does not rename, move, copy, or delete files
- apply asks confirmation by default
- organize asks confirmation by default
- no delete
- no overwrite
- unresolved duplicates are guarded against
- existing target files are skipped
- `--yes` does not bypass safety checks
- logs are written locally under `.pdf-namefix/logs/`

## What It Does Not Do Yet

`pdf-namefix` currently does not support:

- AI-assisted naming
- OCR
- PDF content parsing
- GUI
- cloud sync
- background folder monitoring

See:

```text
docs/KNOWN_LIMITATIONS.md
```

## Collision Handling

`pdf-namefix` resolves suggested filename collisions with numeric suffixes.

Example:

```text
scan.pdf
document.pdf
```

may become:

```text
unknown-date_unknown_document.pdf
unknown-date_unknown_document_2.pdf
```

Safety rules still apply:

- no overwrite
- target exists is skipped
- unresolved duplicate suggestions block apply

## Undo

`pdf-namefix` can undo the latest rename or move operation from local logs.

Undo the latest operation:

```bash
pdf-namefix undo --last
```

Skip confirmation:

```bash
pdf-namefix undo --last --yes
```

Undo from a specific log:

```bash
pdf-namefix undo --log .pdf-namefix/logs/rename-log-20260501T120000Z.jsonl
```

Notes:

- rename operations can be undone
- organize move operations can be undone
- organize copy operations are skipped by default because undoing a copy would delete files
- undo never overwrites existing files

## Install as a CLI

Recommended install method:

```bash
pipx install "git+https://github.com/serkansonmzz/pdf-namefix.git@v0.1.0"
```

Then run:

```bash
pdf-namefix --version
pdf-namefix preview ~/Downloads
```

Uninstall:

```bash
pipx uninstall pdf-namefix
```

For development usage, use `uv run` inside the repository.

## Development

Run tests:

```bash
uv run pytest -q
```

Run the CLI locally:

```bash
uv run pdf-namefix --help
```

## Docs

- `docs/PRODUCT_SCOPE.md`
- `docs/ROADMAP.md`
- `docs/DECISIONS.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/DEMO.md`
- `docs/FIRST_TIME_USER_GUIDE.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/RELEASE_NOTES_v0.1.0.md`
- `docs/INSTALL.md`
- `docs/PACKAGING.md`

## Status

Current release:

```text
v0.1.0 MVP
```

This release includes:

- preview
- safe apply / rename
- PDF organize layer
- edge-case hardening
- README and demo docs

Next stage:

```text
v0.2 Roadmap (Content extraction / Metadata)
```