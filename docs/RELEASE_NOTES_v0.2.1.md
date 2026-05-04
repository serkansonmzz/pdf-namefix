# pdf-namefix v0.2.1 Release Notes

## Status

`pdf-namefix v0.2.1` makes AI suggestions actually useful in the workflow.

## Changes

- AI output now shows current vs improved suggestions
- AI can use practical known-title inference
- Added semantic_type and improvement fields
- Added Markdown AI suggestion reports
- Added JSON AI suggestion reports for apply
- Added preview support for reviewed AI suggestions
- Added apply support for reviewed AI suggestions
- Added `.env.example`
- Improved unknown-only candidate selection

## Workflow

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --unknown-only \
  --format json \
  --out ~/Desktop/ai-suggestions.json \
  --yes

pdf-namefix preview ~/Downloads \
  --ai-suggestions ~/Desktop/ai-suggestions.json

pdf-namefix apply ~/Downloads \
  --ai-suggestions ~/Desktop/ai-suggestions.json
```

## Safety

- AI does not directly rename files
- AI JSON must be explicitly passed to apply
- apply keeps no-overwrite behavior
- undo remains available
