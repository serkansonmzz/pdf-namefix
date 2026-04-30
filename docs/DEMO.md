# pdf-namefix Demo

This document shows a safe local demo flow for `pdf-namefix`.

## Create demo files

```bash
mkdir -p /tmp/pdf-namefix-demo

touch /tmp/pdf-namefix-demo/rust_lifetimes_notes.pdf
touch /tmp/pdf-namefix-demo/clean_architecture_book.pdf
touch /tmp/pdf-namefix-demo/turkcell_fatura_2026-04-29.pdf
touch /tmp/pdf-namefix-demo/agentic_workflows_slides.pdf
touch /tmp/pdf-namefix-demo/random_39281.pdf
```

## Preview

```bash
uv run pdf-namefix preview /tmp/pdf-namefix-demo
```

Expected behavior:

```text
PDF files found: 5
```

The preview command should show:

- detected PDF files
- document type guesses
- suggested filenames
- summary
- collision count
- warning count

Preview does not rename, move, copy, or delete files.

## Verbose preview

```bash
uv run pdf-namefix preview /tmp/pdf-namefix-demo --verbose
```

Verbose mode shows classification and suggestion reasons.

## Apply safe renames

```bash
uv run pdf-namefix apply /tmp/pdf-namefix-demo --yes
```

Expected behavior:

- files are renamed safely
- existing targets are not overwritten
- collisions block apply
- a JSONL log is written under `.pdf-namefix/logs/`

## Organize with copy mode

```bash
uv run pdf-namefix organize /tmp/pdf-namefix-demo \
  --out /tmp/pdf-namefix-organized \
  --copy \
  --yes
```

Check results:

```bash
find /tmp/pdf-namefix-organized -type f
```

Expected folder structure may include:

```text
/tmp/pdf-namefix-organized/books/
/tmp/pdf-namefix-organized/notes/
/tmp/pdf-namefix-organized/invoices/
/tmp/pdf-namefix-organized/slides/
/tmp/pdf-namefix-organized/unknown/
```

## Collision demo

Create colliding files:

```bash
mkdir -p /tmp/pdf-namefix-collision-demo

touch /tmp/pdf-namefix-collision-demo/scan.pdf
touch /tmp/pdf-namefix-collision-demo/document.pdf
```

Run preview:

```bash
uv run pdf-namefix preview /tmp/pdf-namefix-collision-demo
```

Expected behavior:

```text
[COLLISION]
Suggested name collisions: 2
```

Run apply:

```bash
uv run pdf-namefix apply /tmp/pdf-namefix-collision-demo --yes
```

Expected behavior:

```text
Apply blocked because suggested filename collisions were found.
```

No files should be renamed.
