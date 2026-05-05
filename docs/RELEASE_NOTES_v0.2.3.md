# pdf-namefix v0.2.3 Release Notes

## Status

`pdf-namefix v0.2.3` is a practical AI workflow polish release.

## Changes

### Less conservative AI apply threshold

AI suggestions now use the naming profile threshold by default.

Default:

```text
confidence >= 0.70
```

instead of the previous fixed:

```text
confidence >= 0.80
```

This makes practical rename suggestions more useful while still requiring:

- `should_apply=true`
- no-overwrite safety
- user confirmation unless `--yes`
- undo logs

### Better metadata handling

AI instructions now treat PDF metadata as a supporting signal.

The original filename remains the preferred source when it is clear and meaningful.

Example:

```text
SSH-Key-ve-Vps-ayarları.pdf
```

should prefer:

```text
ssh_key_vps_setup_guide.pdf
```

over metadata-driven weak names like:

```text
vite_project_ssh_key_guide.pdf
```

## Safety

This release does not add destructive behavior.

- no delete
- no overwrite
- undo remains available
- AI suggestions still require explicit apply
