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