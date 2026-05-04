# AI-Assisted Naming

`pdf-namefix` supports optional AI-assisted filename suggestions.

AI suggestions are preview/report-only. They do not rename, move, copy, or delete files.

## Setup

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Or create a local `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env`. See `.env.example` for reference.

## Useful AI Suggestions Workflow

### Step 1: Generate AI suggestions

Generate AI suggestions as JSON:

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --unknown-only \
  --format json \
  --out ~/Desktop/ai-suggestions.json \
  --yes
```

Generate AI suggestions as Markdown (for human review):

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --unknown-only \
  --format markdown \
  --out ~/Desktop/ai-suggestions.md \
  --yes
```

By default, this command only sends low-confidence files to AI. Use `--unknown-only` to target only unknown files.

### Step 2: Preview with AI suggestions

Preview what the AI suggestions would look like:

```bash
pdf-namefix preview ~/Downloads \
  --ai-suggestions ~/Desktop/ai-suggestions.json
```

This shows the deterministic preview with AI improvements applied.

### Step 3: Apply AI suggestions

Apply reviewed AI suggestions safely:

```bash
pdf-namefix apply ~/Downloads \
  --ai-suggestions ~/Desktop/ai-suggestions.json
```

This applies only high-confidence AI suggestions (default: 0.80+) while maintaining all safety guarantees.

## Limit the number of files

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --unknown-only \
  --limit 20 \
  --out ai-suggestions.json
```

## Use a naming profile

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --profile examples/naming-profile.example.yml \
  --out ai-suggestions.json
```

## Safety

- AI suggestions are generated first and saved to a file.
- You review the JSON or Markdown report.
- Apply reads from the reviewed JSON file.
- Apply still uses no-overwrite and undo-safe behavior.
- AI confidence threshold controls which suggestions are applied.

## Privacy

AI-assisted naming sends selected filename, metadata, and first-page text signals to a remote model provider.

Do not use AI-assisted naming on sensitive documents unless you intentionally accept that data flow.

## Format differences

### JSON format

Machine-readable. Can be passed to `apply --ai-suggestions`.

### Markdown format

Human-readable. Shows current vs AI suggestion side-by-side.

Use Markdown for review, JSON for apply.
