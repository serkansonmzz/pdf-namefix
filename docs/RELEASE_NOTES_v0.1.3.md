# Release Notes - v0.1.3 (Phase 13)

This release focuses on hardening `pdf-namefix` for real-world file system chaos based on actual user feedback.

## Added
- **Unknown Skip**: `apply` now safely skips files classified as `unknown` or with low confidence (< 0.7) by default. Added `--include-unknown` and `--min-confidence` flags to override this behavior.
- **Preview Filtering**: Added `--summary-only`, `--only <type>`, and `--limit <number>` to `preview` to make large folders manageable in the terminal.
- **Disk Safety**: `organize --copy` now performs a pre-flight disk space check and blocks execution if there isn't enough space to copy the PDFs.
- **Nested Path Safety**: `organize` now blocks running if the `--out` target directory is inside the scanned input directory, preventing recursive scanning issues. Added `--allow-nested-output` to bypass.
- **Expanded Classifier**: Added many new document types (`VISA`, `CV`, `STUDENT_DOCUMENT`, `EXAM`, `MEDICAL`, `PAYMENT`, `REFERENCE`, `LANGUAGE_LEARNING`, `STUDY_MATERIAL`, `NOVEL`, `WHITEPAPER`) and improved Turkish/English keywords based on real-world datasets.

## Fixed
- Prevented potential data loss or half-copied folders due to out-of-disk-space errors during `organize --copy`.
- Stopped `unknown` documents from being forcefully renamed into generic `unknown-date_unknown_document.pdf` names.

## Technical Details
- Added `pdf_namefix.safety` module for disk and path validation.
- Updated `DocumentType` enum in `models.py` to support a wider array of real-world documents.
- Refactored `preview_report.py` to support filtering logic.
- Increased test coverage for new CLI options, safety checks, and the expanded classifier rules.
