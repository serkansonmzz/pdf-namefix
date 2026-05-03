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

Do not commit `.env`.

## Generate AI suggestions

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
  --out ai-suggestions.json
```

By default, this command only sends unknown or low-confidence files to AI.

## Limit the number of files

```bash
pdf-namefix ai-suggest ~/Downloads \
  --inspect-pdf \
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

AI suggestions are not automatically applied.

Review `ai-suggestions.json` before using any suggestion in a later workflow.

## Privacy

AI-assisted naming sends selected filename, metadata, and first-page text signals to a remote model provider.

Do not use AI-assisted naming on sensitive documents unless you intentionally accept that data flow.

## Current limitations

- AI suggestions are not integrated into `apply` yet.
- This command creates a suggestions JSON file only.
- API usage may cost money depending on your provider and model.
- Only metadata and first-page text signals are sent.
- AI output can still be wrong and must be reviewed.
