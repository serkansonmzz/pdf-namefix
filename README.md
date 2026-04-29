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