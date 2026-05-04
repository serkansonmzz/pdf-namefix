# Phase 18 - Real-World Cleanup Intelligence - IMPLEMENTATION SPEC

## 📋 Overview

**Amaç:** Real-world cleanup kalitesini yükseltmek ve gerçek kullanımda görülen sorunları çözmek.

**Sürüm:** v0.2.2 (minor release)

**Branch:** `feature/real-world-cleanup-intelligence`

---

## 🎯 Ana Hedefler

Bu faz, projenin "gerçek klasör temizleme" kalitesini yükseltir. Şu anki sorunlar:

1. ❌ Low-confidence dosyaları AI'a gitmiyor
2. ❌ Organize bazı dosyaları yanlışlıkla unknown/ içine atıyor
3. ❌ `unknown-date_` prefix bazı dosyalarda çirkin duruyor
4. ❌ Rename edilmiş dosyanın type bilgisi organize aşamasında kayboluyor
5. ❌ Kullanıcı kendi naming/folder tercihlerini veremiyor

---

## 📁 Değişecek/Eklenecek Dosyalar

### Yeni Dosyalar
- ✨ `src/pdf_namefix/type_resolver.py` - Type suffix resolver
- ✨ `tests/test_type_resolver.py` - Type resolver testleri

### Güncellenecek Dosyalar
- 🔧 `src/pdf_namefix/models.py` - NamingProfile genişletme
- 🔧 `src/pdf_namefix/naming_profile.py` - Config sisteme
- 🔧 `src/pdf_namefix/name_suggester.py` - Profile-based naming
- 🔧 `src/pdf_namefix/ai_naming.py` - Profile-aware prompt
- 🔧 `src/pdf_namefix/apply_ai_suggestions.py` - Type preservation
- 🔧 `src/pdf_namefix/organizer.py` - Profile-based folders
- 🔧 `src/pdf_namefix/classifier.py` - Suffix resolver integration
- 🔧 `src/pdf_namefix/cli.py` -- Profile support
- 🔧 `examples/naming-profile.example.yml` - Full config
- 🔧 `tests/test_naming_profile.py` - New field tests
- 🔧 `tests/test_name_suggester.py` - Unknown-date tests
- 🔧 `tests/test_ai_naming.py` - Low-confidence tests
- 🔧 `tests/test_organizer.py` - Folder map tests
- 🔧 `tests/test_cli.py` - Integration tests
- 🔧 `README.md` - Real-world workflow
- 🔧 `docs/AI_NAMING.md` - Low-confidence workflow
- 🔧 `docs/DECISIONS.md` - 4 yeni decision
- 🔧 `docs/RELEASE_NOTES_v0.2.2.md` - Release notes

---

## 🔧 Implementasyon Adımları

### Adım 1: Git Branch Oluşturma
```bash
git switch main
git pull origin main
git switch -c feature/real-world-cleanup-intelligence
git branch --show-current  # Verify: feature/real-world-cleanup-intelligence
```

### Adım 2: NamingProfile'ı Config Sisteme Çevir
`DEFAULT_NAMING_PROFILE` güncelle:
- `pattern: "{title}_{type}"` (date yok)
- `date_fallback: "none"`
- `include_unknown_date_prefix: False`
- `include_type_suffix: True`
- `low_confidence_threshold: 0.70`
- `folders: dict[str, str]` - Type to folder mapping
- Default unknown folder: `"needs-review"`

NamingProfile dataclass'a yeni alanlar ekle:
- `include_unknown_date_prefix: bool`
- `include_type_suffix: bool`
- `low_confidence_threshold: float`
- `folders: dict[str, str]`

### Adım 3: examples/naming-profile.example.yml Güncelle
Yeni profile yapısı:
- `include_unknown_date_prefix: false`
- `include_type_suffix: true`
- `low_confidence_threshold: 0.70`
- `folders` mapping tüm type'lar için

### Adım 4: name_suggester.py - Profile'a Bağla
- `suggest_filename()` fonksiyonuna `profile` parametresi ekle
- `unknown-date_` prefix mantığını profile'a bağla
- Type suffix'i profile'a bağla
- Pattern'i profile'dan kullan

Sonuç:
```text
atomic_habits_ebook.pdf  (yeni)
unknown-date_atomic_habits_ebook.pdf  (eski)
```

### Adım 5: CLI'ya --profile Desteği Ekle
`preview`, `apply`, `organize` komutlarına:
- `--profile` option ekle
- `load_naming_profile(profile)` kullan
- Profile'ı `suggest_filenames` ve organizer'a geçir

### Adım 6: Low-Confidence AI Pass Default Yap
`ai-suggest` command'de:
- Eğer `--unknown-only` veya `--low-confidence` yoksa: default = `--low-confidence`
- Terminal output'ta açık göster
- Profile'dan `low_confidence_threshold` kullan

Bu sayede düşük confidence dosyaları AI'a gider:
```text
How_To_Stop_Worrying_And_Start_Living.pdf
Made To Stick PDF.pdf
Neovim-ve-Tmux-kurulumu.pdf
```

### Adım 7: Type Resolver Ekle
`src/pdf_namefix/type_resolver.py` oluştur:
- `document_type_from_filename_suffix()` fonksiyonu
- Tüm type suffix'lerini map et: `_book.pdf`, `_study_material.pdf`, vb.

### Adım 8: Classifier'da Suffix Resolver Kullan
`classify_pdf_file` başında:
- Suffix resolver'ı çalıştır
- Eğer type bulunursa ve UNKNOWN değilse, direkt dön
- High confidence (0.95) ver

Örnek:
```text
baglantili_not_almanin_faydasi_study_material.pdf
→ study_material confidence=0.95
```

### Adım 9: Organizer'da Folder Map Profile'dan Gel
`folder_for_document_type()` fonksiyonu:
- Profile'dan gelen folders dict'i kullan
- Fallback: `TYPE_FOLDER_MAP`

`build_organize_plan()` imzası:
- `folders: dict[str, str] | None` parametresi ekle

Default unknown folder: `needs-review`

### Adım 10: Organize Komutuna --inspect-pdf Ekle
Eğer yoksa `--inspect-pdf` option ekle
- PDF metadata/text ile classification iyileştir
- Suffix resolver zaten hızlı yakalayacak

### Adım 11: AI Prompt'u Profile-Aware Yap
`ai_naming.py` prompt'ta:
- `include_unknown_date_prefix` bilgisini ekle
- `include_type_suffix` bilgisini ekle
- Date fallback davranışını açıkla

### Adım 12: Test Dosyaları Oluştur ve Güncelle
- `test_naming_profile.py` - Yeni alanlar için testler
- `test_name_suggester.py` - Unknown-date kalktı mı?
- `test_type_resolver.py` - Yeni test dosyası
- `test_classifier.py` - Suffix resolver integration
- `test_organizer.py` - Folder map tests
- `test_cli.py` - Integration tests
- `test_ai_naming.py` - Low-confidence tests

### Adım 13: Dokümantasyon Güncelle
- `README.md` - Real-world workflow section
- `docs/AI_NAMING.md` - Low-confidence workflow
- `docs/DECISIONS.md` - 4 yeni decision
- `docs/RELEASE_NOTES_v0.2.2.md` - Release notes

---

## 🧪 Test Planı

### Unit Tests
- ✅ Profile yeni alanlar yükleniyor
- ✅ Unknown-date prefix default yok
- ✅ Gerçek tarih korunuyor
- ✅ Type suffix'ler doğru çözülüyor
- ✅ Classifier suffix resolver kullanıyor
- ✅ Organizer folder map kullanıyor
- ✅ Unknown folder → needs-review
- ✅ AI default low-confidence seçiyor

### Manual Tests
- ✅ Preview clean filenames gösteriyor
- ✅ AI low-confidence dosyaları seçiyor
- ✅ Apply AI suggestions kullanıyor
- ✅ Organize type suffix'ten klasör seçiyor
- ✅ needs-review klasörü kullanılıyor

---

## 📝 Beklenen Çıktı

### Filename Öncesi:
```text
unknown-date_atomic_habits_pdfdrive_ebook.pdf
unknown-date_the_war_of_art_robert_pressfield_book.pdf
unknown-date_how_to_lie_with_statistics_book.pdf
```

### Filename Sonrası:
```text
atomic_habits_ebook.pdf
the_war_of_art_robert_pressfield_book.pdf
how_to_lie_with_statistics_book.pdf
```

### Organize Öncesi:
```text
OrganizedPDFs/unknown/baglantili_not_almann_faydas_study_material.pdf
OrganizedPDFs/unknown/morphological_lexical_language_learning.pdf
OrganizedPDFs/unknown/fonksiyonlar_quiz_payment.pdf
```

### Organize Sonrası:
```text
OrganizedPDFs/study-materials/baglantili_not_almann_faydas_study_material.pdf
OrganizedPDFs/language-learning/morphological_lexical_language_learning.pdf
OrganizedPDFs/payments/fonksiyonlar_quiz_payment.pdf
```

---

## 🔄 Recommended Real-World Workflow

```bash
# 1. Inspect and summarize
pdf-namefix preview ~/Downloads --inspect-pdf --summary-only

# 2. Generate AI suggestions for low-confidence files
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --low-confidence \
  --format json \
  --out ~/Desktop/ai-low-confidence.json \
  --yes

# 3. Preview with AI suggestions
pdf-namefix preview ~/Downloads \
  --inspect-pdf \
  --ai-suggestions ~/Desktop/ai-low-confidence.json

# 4. Apply reviewed suggestions
pdf-namefix apply ~/Downloads \
  --inspect-pdf \
  --ai-suggestions ~/Desktop/ai-low-confidence.json

# 5. Organize
pdf-namefix organize ~/Downloads \
  --inspect-pdf \
  --out ~/Documents/OrganizedPDFs
```

---

## ⚠️ Güvenlik Notları

- ✅ AI default low-confidence ama hala kullanıcı kontrolünde
- ✅ Unknown-date prefix configurable
- ✅ Folder mapping customizable
- ✅ Suffix resolver sadece kontrollü rename pipeline'dan gelen type'ları kabul eder
- ✅ Organize güvenli kopyalama/taşıma davranışını korur

---

## 🚀 Son Adımlar

1. Tüm testleri çalıştır
2. Manual sandbox test
3. Code review
4. Commit: `git commit -m "feat: real-world cleanup intelligence"`
5. (Sonraki adımda) PR ve merge

---

**Spec Hazırlayan:** Claude Code
**Tarih:** 2026-05-04
**Durum:** ONAY BEKLIYOR