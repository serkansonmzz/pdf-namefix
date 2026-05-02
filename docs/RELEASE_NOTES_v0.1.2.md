# pdf-namefix v0.1.2 Release Notes

## Status

`pdf-namefix v0.1.2` adds safer apply behavior and undo recovery.

## Changes

### Collision suffixing

Suggested filename collisions are now resolved with numeric suffixes.

Example:

```text
scan.pdf
document.pdf
```

can become:

```text
unknown-date_unknown_document.pdf
unknown-date_unknown_document_2.pdf
```

### Undo

Added undo support:

```bash
pdf-namefix undo --last
```

Undo supports:

- rename operations
- organize move operations

Undo skips:

- copied files, because deleting copies is not enabled by default
- missing targets
- cases where the original source path already exists

## Safety

- no delete
- no overwrite
- copy undo is skipped by default
- unresolved duplicates are guarded against
- undo is based on local JSONL logs

## Verify

```bash
pdf-namefix --version
pdf-namefix preview ~/Downloads
pdf-namefix apply ~/Downloads
pdf-namefix undo --last
```
