# Release Notes - v0.1.4 (Phase 14)

This release breaks the filename-only boundary and introduces local PDF inspection to significantly reduce the number of "unknown" classifications.

## Added
- **PDF Inspection (`--inspect-pdf`)**: A new opt-in flag for `preview`, `apply`, and `organize` commands that reads PDF metadata (title, author, subject) and the extractable text from the first page to improve classification accuracy.
- Support for recognizing PDFs based on metadata or page content, falling back gracefully if the PDF is broken, encrypted, or simply an image scan.

## Technical Details
- Added `pypdf` dependency.
- Created `PdfInsights` model to represent extracted metadata and text.
- Created `pdf_inspector.py` to safely extract data from PDFs without crashing the main process on bad files.
- Updated `classifier.py` to evaluate `PdfInsights` (if available) with a confidence score of 0.75 when filename rules fail.
- Inspection is strictly local and does not use OCR, AI, or cloud services.
