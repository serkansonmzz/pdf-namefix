# Release Notes v0.2.2 - Real-World Cleanup Intelligence

**Release Date:** 2026-05-04

## Overview

Phase 18 focuses on solving real-world cleanup problems observed in actual usage. This release makes filenames cleaner, organization smarter, and gives users more control through profile-based configuration.

## Major Changes

### 1. Cleaner Filenames (No More `unknown-date_` Prefix)

**Before:**
```
unknown-date_atomic_habits_ebook.pdf
unknown-date_clean_architecture_book.pdf
```

**After:**
```
atomic_habits_ebook.pdf
clean_architecture_book.pdf
```

The `unknown-date_` prefix is now disabled by default. You can enable it in your profile if needed:
```yaml
include_unknown_date_prefix: true
date_fallback: "unknown-date"
```

### 2. Type Suffix Recovery for Smarter Organization

The classifier now checks filename suffixes FIRST with 0.95 confidence. This means:
- Files renamed as `atomic_habits_book.pdf` will be organized into `books/` folder
- Files renamed as `python_course_study_material.pdf` will go to `study-materials/`
- No more losing type information after rename!

**Supported suffixes** (22 types):
- `_book.pdf`, `_ebook.pdf` → books
- `_invoice.pdf`, `_fatura.pdf` → invoices
- `_notes.pdf`, `_not.pdf` → notes
- `_study_material.pdf` → study-materials
- `_language_learning.pdf` → language-learning
- And 16 more...

### 3. Profile-Based Folder Mapping

Customize where each document type goes:

```yaml
folders:
  book: books
  ebook: my-library
  unknown: needs-review  # Changed from "unknown"
  invoice: invoices/turkcell
  notes: my-notes
```

### 4. Updated Default Naming Pattern

**Old pattern:** `{date}_{title}_{type}`
**New pattern:** `{title}_{type}`

This produces cleaner filenames:
```
atomic_habits_book.pdf        # Before: unknown-date_atomic_habits_book.pdf
clean_architecture_book.pdf   # Before: 2026-05-04_clean_architecture_book.pdf
```

### 5. Needs-Review Folder

Unknown files now go to `needs-review/` instead of `unknown/` - clearer about what requires attention.

## Configuration Examples

### Minimal Configuration (New Defaults)

```yaml
# ~/.pdf-namefix/profile.yml
language: english
pattern: "{title}_{type}"
date_fallback: "none"
include_unknown_date_prefix: false
include_type_suffix: true
```

### Turkish Profile with Custom Folders

```yaml
language: turkish
pattern: "{title}_{type}"
date_fallback: "none"
include_unknown_date_prefix: false
include_type_suffix: true
folders:
  invoice: faturalar
  book: kitaplik
  unknown: incelenecek
  notes: notlarim
```

### Date Prefix Enabled (Old Behavior)

```yaml
date_fallback: "unknown-date"
include_unknown_date_prefix: true
```

## CLI Enhancements

All major commands now support `--profile` option:

```bash
# Preview with custom profile
pdf-namefix preview ./docs --profile ~/my-profile.yml

# Apply with profile
pdf-namefix apply ./docs --profile ~/my-profile.yml --yes

# Organize with custom folder mapping
pdf-namefix organize ./docs --out ./organized --profile ~/my-profile.yml
```

## AI Improvements

AI prompts are now profile-aware:
- Respects `include_unknown_date_prefix` setting
- Respects `include_type_suffix` setting
- Better filename suggestions based on profile

## Migration Guide

### For Existing Users

1. **Default behavior changed:** Your filenames will be cleaner (no `unknown-date_` prefix)
2. **Unknown folder renamed:** `unknown/` → `needs-review/`
3. **Pattern changed:** `{date}_{title}_{type}` → `{title}_{type}`

### To Keep Old Behavior

Create `~/.pdf-namefix/profile.yml`:
```yaml
date_fallback: "unknown-date"
include_unknown_date_prefix: true
pattern: "{date}_{title}_{type}"
folders:
  unknown: unknown
```

## Test Results

- **All 171 tests passing** ✓
- Test coverage maintained at 100%
- New `type_resolver.py` module fully tested

## Breaking Changes

1. **Default pattern changed** - Filenames will be shorter by default
2. **Unknown folder renamed** - Organize commands use `needs-review/` instead of `unknown/`
3. **Filename format** - Files without dates will no longer get `unknown-date_` prefix

## Decisions Made

1. **Date prefix removal:** Real-world usage showed this makes filenames noisy
2. **Needs-review folder:** "unknown" doesn't tell users what action to take
3. **Type suffix recovery:** Prevents losing classification after rename
4. **Profile-first config:** Enables customization without code changes

## Next Steps

See [SPEC_PHASE18.md](SPEC_PHASE18.md) for implementation details.

## Upgrade Instructions

```bash
# Install update
pip install --upgrade pdf-namefix

# Optional: Create custom profile
mkdir -p ~/.pdf-namefix
cp examples/naming-profile.example.yml ~/.pdf-namefix/profile.yml
# Edit ~/.pdf-namefix/profile.yml to your needs

# Verify installation
pdf-namefix --version
pdf-namefix preview ./test-folder --dry-run
```

## Support

- GitHub Issues: https://github.com/serkansonmez/pdf-namefix/issues
- Documentation: See README.md and docs/ folder

---

**Full Changelog:**
- Added: Profile-based configuration system (naming_profile.py)
- Added: Type suffix resolver (type_resolver.py) with 22 type patterns
- Changed: Default pattern from `{date}_{title}_{type}` to `{title}_{type}`
- Changed: Default `date_fallback` from "unknown-date" to "none"
- Changed: Default `include_unknown_date_prefix` to false
- Changed: Unknown folder from "unknown" to "needs-review"
- Updated: AI prompts to be profile-aware
- Updated: CLI with --profile support for preview, apply, organize
- Updated: All 171 tests for new filename format
- Fixed: Type information preservation after rename operations
