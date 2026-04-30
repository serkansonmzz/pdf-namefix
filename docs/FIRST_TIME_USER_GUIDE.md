# First-Time User Guide

This guide shows the safest way to try `pdf-namefix`.

## 1. Start with preview

Never start with apply.

Use:

```bash
uv run pdf-namefix preview ~/Downloads
```

This command only reads and prints information.

It does not rename, move, copy, or delete files.

## 2. Check the summary

Look at:

```text
Unknown type
Suggested name collisions
Warnings
```

If collisions exist, do not apply renames yet.

## 3. Use verbose mode if needed

```bash
uv run pdf-namefix preview ~/Downloads --verbose
```

Verbose mode explains why a type or filename suggestion was produced.

## 4. Apply renames only after preview

```bash
uv run pdf-namefix apply ~/Downloads
```

This asks for confirmation by default.

To skip confirmation:

```bash
uv run pdf-namefix apply ~/Downloads --yes
```

`--yes` does not bypass safety checks.

## 5. Organize safely with copy mode first

For first-time usage, prefer copy mode:

```bash
uv run pdf-namefix organize ~/Downloads \
  --out ~/Documents/OrganizedPDFs \
  --copy
```

This keeps original files in place.

## 6. Use move mode after you trust the output

```bash
uv run pdf-namefix organize ~/Downloads \
  --out ~/Documents/OrganizedPDFs
```

Move mode removes files from the source folder after moving them to the output folder.

## 7. Logs

Apply and organize operations write logs under:

```text
.pdf-namefix/logs/
```

These logs are local and should not be committed to Git.

## 8. Current limitations

See:

```text
docs/KNOWN_LIMITATIONS.md
```
