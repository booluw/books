# CLAUDE.md

Guidance for Claude Code sessions working in this repository.

## Git commits

- **Author every commit as the repository owner:** `Boluwatife Johnson <boluwatife.j.johnson@gmail.com>`.
  A SessionStart hook in `.claude/settings.json` sets this as the repo's git `user.name` and `user.email`. Before committing, check with `git config user.name` and `git config user.email`. If they differ, set them to the values above.
- **Do not add a `Co-Authored-By` trailer** to commit messages.

## What this repository is

Book-length research guides, one book per top-level folder. Follow the layout and writing conventions in [`README.md`](README.md):

- Each book has its own folder with `chapters/`, `appendices/`, `diagrams/`, `examples/`, `exercises/` and `templates/` as its subject needs.
- Write for a technical reader who is new to the subject: define every term the first time it appears, and explain why before how.
- Date facts that change over time (versions, vendors, regulations, salaries), and list sources in the book's bibliography.
- Keep examples runnable with minimal dependencies; each example folder has a README, and tests run with `python3 <book>/examples/run_all_tests.py` where present.
- Diagrams are Mermaid; quote node labels that contain punctuation and use `<br/>` for line breaks.
