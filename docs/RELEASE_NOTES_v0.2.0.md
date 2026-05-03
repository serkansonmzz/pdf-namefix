# pdf-namefix v0.2.0 Release Notes

## Status

`pdf-namefix v0.2.0` adds optional AI-assisted naming suggestions.

## Changes

### AI-assisted naming

Added:

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --out ai-suggestions.json
```

### Naming profile

Added support for configurable naming rules through a YAML profile.

Example:

```bash
pdf-namefix ai-suggest ~/Downloads \
  --profile examples/naming-profile.example.yml \
  --out ai-suggestions.json
```

## Safety

- AI is opt-in.
- AI does not rename files.
- AI does not move files.
- AI does not delete files.
- AI suggestions are written to JSON for review.
- Default candidates are unknown or low-confidence files.

## Privacy

AI-assisted naming sends selected filename, metadata, and first-page text signals to the configured AI provider.

Do not use AI-assisted naming on sensitive documents unless intentional.
