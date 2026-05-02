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

## Decision 018: Downloads Cleaner stays PDF-focused

The organize command only organizes discovered PDF files.

Reason:

The project should not become a general-purpose file cleaner in v0.1.

## Decision 019: Organize supports both move and copy

The default mode is move, while `--copy` keeps original files.

Reason:

Move is useful for cleanup, but copy is safer for first-time usage and testing.

## Decision 020: Organize never overwrites target files

If the target file already exists, the item is skipped.

Reason:

A file organization tool must never overwrite user files silently.

## Decision 021: Phase 8 focuses on hardening, not new features

Phase 8 adds edge-case tests, safer source existence checks, known limitations, and small reliability improvements.

Reason:

The MVP already has preview, apply, and organize. Before adding more features, the current behavior should be made safer.

## Decision 022: Missing source files are skipped

If a file disappears between scan and apply/organize planning, the item is skipped.

Reason:

Filesystem state can change between discovery and execution. The tool should not crash or produce unsafe behavior.

## Decision 023: Phase 9 focuses on user-facing documentation

Phase 9 improves README, demo instructions, first-time usage guidance, and GitHub presentation.

Reason:

The tool already has core MVP behavior. Before release, users need to understand how to install, run, and safely use it.

## Decision 024: First-time users should prefer preview and copy mode

Documentation recommends preview first and organize with `--copy` first.

Reason:

The safest first experience should be non-destructive and reversible by simply deleting copied output.

## Decision 025: v0.1.0 supports GitHub-based pipx installation first

`pdf-namefix` will first support installation from GitHub using `pipx`.

Reason:

Publishing to PyPI is useful, but GitHub-based pipx installation is enough for the first release and avoids premature package registry work.

## Decision 026: PyPI publishing is postponed

PyPI publishing is not part of v0.1.0.

Reason:

The package should first prove its installability and CLI behavior via GitHub releases and pipx.

## Decision 027: Suggested filename collisions are resolved with numeric suffixes

When multiple files produce the same suggested filename, `pdf-namefix` appends numeric suffixes such as `_2`, `_3`.

Reason:

Blocking all collisions is safe but too strict for real Downloads folders. Numeric suffixing keeps apply useful while preserving no-overwrite behavior.

## Decision 028: Undo supports rename and move, but not copy deletion by default

Undo can reverse rename operations and organize move operations.

Copy operations are skipped by default.

Reason:

Undoing a copy would require deleting the copied file, which conflicts with the current no-delete safety model.

## Decision 029: Unknown files are skipped by default during apply

Files classified as `unknown` or those below a confidence threshold (0.7) are not renamed by default.

Reason:

Real-world usage showed high "unknown" rates. Renaming important, unclassifiable documents to `unknown-date_unknown_document.pdf` is undesirable.

## Decision 030: Preview supports filtering and limits

Preview supports `--only`, `--limit`, and `--summary-only`.

Reason:

Real-world folders contain hundreds of PDFs. Long terminal outputs become unreadable. Users need a way to filter noise.

## Decision 031: Organize copy checks disk space

Before running a copy operation, `pdf-namefix` checks if enough free space exists on the target disk.

Reason:

Copying hundreds of large PDFs can exhaust disk space, causing mid-operation failures. Early validation is safer.

## Decision 032: Organize blocks nested outputs

`organize` will block an `--out` directory if it is a child of the input folder unless `--allow-nested-output` is given.

Reason:

Placing the organized folder inside the scanned folder can cause recursive scanning loops or confusion in subsequent runs.