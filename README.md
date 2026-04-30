# pdf-namefix

A small, local-first CLI tool for previewing and safely renaming messy PDF files.

`pdf-namefix` scans one or more folders, detects PDF files, suggests cleaner names based on simple local rules, and only renames files after explicit user action.

The first version is intentionally simple:

- AI-free
- OCR-free
- preview-first
- local-only
- safe by default
- focused on PDF files
- designed for multi-folder scanning
- built with future AI-assisted naming in mind

## Why this exists

PDF folders get messy fast.

Examples:

```text
scan_239812.pdf
document-final-v3.pdf
whatsapp-document-2026.pdf
rust-notes-unknown.pdf
invoice123.pdf
```

## PDF Scanner

Phase 2 adds safe PDF discovery.

```bash
uv run pdf-namefix preview ~/Downloads
uv run pdf-namefix preview ~/Downloads ~/Desktop
uv run pdf-namefix preview ~/Downloads --recursive
```

The scanner:

- finds `.pdf` and `.PDF` files
- supports multiple input paths
- supports optional recursive scanning
- ignores non-PDF files
- avoids duplicate files
- reports warnings without renaming anything

## Document Type Classifier

Phase 3 adds a simple filename-based document type classifier.

The classifier is intentionally local and deterministic.

It currently supports types such as:

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

Example:

```bash
uv run pdf-namefix preview ~/Downloads
```

Possible output:

```text
PDF files found: 3

1. /Users/me/Downloads/rust_lifetimes_notes.pdf (120.0 KB) [notes] confidence=0.9
2. /Users/me/Downloads/clean_architecture_book.pdf (5.2 MB) [book] confidence=0.9
3. /Users/me/Downloads/random_scan.pdf (84.1 KB) [document] confidence=0.3
```

Phase 3 does not inspect PDF content yet.  
Classification is based on filenames only.

## Filename Suggestions

Phase 4 adds safe filename suggestions.

The tool now scans PDFs, classifies them by filename, and suggests cleaner names without renaming anything.

Example:

```bash
uv run pdf-namefix preview ~/Downloads
```

Possible output:

```text
PDF files found: 3

1. /Users/me/Downloads/rust_lifetimes_notes.pdf (120.0 KB) [notes] confidence=0.9
   → unknown-date_rust_lifetimes_notes.pdf

2. /Users/me/Downloads/clean_architecture_book.pdf (5.2 MB) [book] confidence=0.9
   → unknown-date_clean_architecture_book.pdf

3. /Users/me/Downloads/turkcell_fatura_2026-04-29.pdf (90.0 KB) [invoice] confidence=0.9
   → 2026-04-29_turkcell_fatura_invoice.pdf
```

Phase 4 still does not rename, move, copy, or delete files.

## Preview Hardening

Phase 5 improves the preview command with:

- summary output
- unknown type count
- warning count
- suggested filename collision detection
- optional verbose reasons

Example:

```bash
uv run pdf-namefix preview ~/Downloads --verbose
```

Possible output:

```text
PDF files found: 2

1. /Users/me/Downloads/scan.pdf (10.0 KB) [document] confidence=0.3 [COLLISION]
   → unknown-date_unknown_document.pdf
   classification: Matched generic keyword: scan
   suggestion: Built from filename date, cleaned title slug, and classified document type.

2. /Users/me/Downloads/document.pdf (11.0 KB) [document] confidence=0.3 [COLLISION]
   → unknown-date_unknown_document.pdf

Summary
- Total PDF files: 2
- Unknown type: 0
- Suggested name collisions: 2
- Warnings: 0
```

Phase 5 still does not rename, move, copy, or delete files.

## CLI Preview

Phase 1 introduces the initial CLI skeleton.

```bash
uv run pdf-namefix --help
uv run pdf-namefix --version
uv run pdf-namefix preview ~/Downloads
uv run pdf-namefix apply ~/Downloads
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs
```