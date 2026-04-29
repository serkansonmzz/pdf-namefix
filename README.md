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

## CLI Preview

Phase 1 introduces the initial CLI skeleton.

```bash
uv run pdf-namefix --help
uv run pdf-namefix --version
uv run pdf-namefix preview ~/Downloads
uv run pdf-namefix apply ~/Downloads
uv run pdf-namefix organize ~/Downloads --out ~/Documents/OrganizedPDFs
```