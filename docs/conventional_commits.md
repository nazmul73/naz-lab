# Naz Lab Commit Message Policy

Use conventional commit prefixes for all new changes so future repo history is readable.

## Required prefixes

```text
feat: new user-facing feature or workflow
fix: bug fix or runtime stability improvement
docs: documentation, markers, launcher notes
chore: dependency, package, repo hygiene, cleanup
refactor: code structure change without behavior change
test: smoke checks or validation helpers
```

## Examples

```text
feat: add Drive-backed chat autosave
fix: harden Ollama Drive symlink persistence
docs: clarify single official dashboard launcher
chore: update image workstation requirements
refactor: make root app redirect to official dashboard
test: add backend smoke check helper
```

## Rule

Do not use blank commit messages. Each commit should explain the change area and reason in one concise line.
