# pdf-namefix Decisions

## Decision 001: v0.1 is AI-free

v0.1 will not use AI.

Reason:

The first version should be local, predictable, cheap, and safe. AI can be added later after the deterministic workflow is stable.

## Decision 002: v0.1 is OCR-free

v0.1 will not use OCR.

Reason:

OCR adds installation complexity, performance cost, and platform-specific issues. The first version should rely on filenames, metadata, and extractable text when available.

## Decision 003: Preview-first behavior

The default command should preview suggested changes before applying them.

Reason:

Renaming files is potentially destructive from a user-trust perspective. The user should see what will happen before any file is touched.

## Decision 004: No automatic delete

The tool will not delete files in v0.1.

Reason:

File deletion increases risk and is not required for the first useful version.

## Decision 005: Downloads Cleaner is an internal layer, not a separate project

The Downloads Cleaner idea will be implemented as an organize feature inside `pdf-namefix`.

Reason:

The main user need is PDF organization. Keeping it inside the same project reduces context switching and keeps the tool focused.

## Decision 006: Prefer unknown over wrong confidence

If the tool cannot confidently classify a document, it should use `unknown` or `document`.

Reason:

A safe unclear result is better than a confident wrong rename.

## Decision 007: Multiple folders should be supported early

The CLI should allow more than one path.

Reason:

Users often keep PDFs across Downloads, Desktop, Documents, and project folders.

## Decision 008: Phase 3 classifier is filename-based

The first document type classifier will use filename keywords only.

Reason:

This keeps the first classification layer local, predictable, testable, and AI-free.

PDF content extraction, metadata parsing, OCR, and AI-assisted classification are future improvements.

## Decision 009: Phase 4 suggestions are preview-only

Filename suggestions will be shown in preview mode first.

Reason:

Renaming files is risky. Users should see proposed names before any apply/rename command exists.

## Decision 010: Unknown date is explicit

If no date can be extracted from the filename, the suggestion will use `unknown-date`.

Reason:

A missing date should be visible instead of silently inventing a date.

## Decision 011: Suggested names are conservative

Suggested names are built from:

- extracted filename date,
- cleaned filename title,
- classified document type.

Reason:

v0.1 should avoid AI/OCR complexity and keep naming deterministic.

## Decision 012: Phase 5 detects collisions but does not resolve them

Preview will mark suggested filename collisions.

Reason:

Users should see unsafe rename situations before apply exists. Collision resolution will be handled later in the safe apply/rename flow.

## Decision 013: Preview summary is required before apply

Preview should show total files, unknown type count, collision count, and warning count.

Reason:

Renaming files should be based on a clear summary, not only a long list of suggestions.

## Decision 014: Verbose mode shows reasons

Preview supports `--verbose` to show classification and suggestion reasons.

Reason:

The default output should stay readable, but users and developers need a way to inspect why a suggestion was produced.

## Decision 015: Apply is blocked when suggested filename collisions exist

If two or more files produce the same suggested filename, apply exits without renaming files.

Reason:

Collision resolution should be explicit. The first safe apply flow should never risk overwriting or ambiguous renames.

## Decision 016: Apply writes a rename log

Every apply run writes a JSONL log under `.pdf-namefix/logs/`.

Reason:

Renaming files changes the local filesystem. Users need an audit trail for what happened.

## Decision 017: Apply asks for confirmation by default

The apply command requires interactive confirmation unless `--yes` is passed.

Reason:

Preview-first and confirmation-first behavior reduces accidental renames.