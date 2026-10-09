# Books

This repository holds book-length research. Each book is a self-contained guide to a single subject.

## Layout convention

Every book lives in its own top-level folder, named in `kebab-case` after its subject. Inside it:

```
<book-name>/
├── README.md        # Title page, audience, how to read, full table of contents
├── chapters/        # The main text, one Markdown file per chapter (NN-slug.md)
├── appendices/      # Glossary, bibliography, checklists, reference tables
├── diagrams/        # Mermaid (.md) diagrams, referenced from chapters
├── examples/        # Runnable code and artefacts that chapters walk through
├── exercises/       # Exercises per chapter, with worked solutions
└── templates/       # Reusable documents the reader can copy into real work
```

Not every book needs every folder. A book adds folders when its subject needs them, for example `case-studies/` or `datasets/`.

## Writing conventions

- **Audience:** the reader is technical but new to the subject. Every term is defined the first time it appears, and the text explains *why* before *how*.
- **Currency:** facts that change over time, such as versions, standards status, vendor landscape and salaries, carry the date they were checked. Each book's bibliography lists its sources.
- **Runnable examples:** code in `examples/` runs with as few dependencies as possible, and each example folder has a README with instructions.

## Books

| Book | Folder | Status |
|---|---|---|
| *The Integration Design Engineer: A Field Guide to Connecting Systems* | [`integration-design-engineer/`](integration-design-engineer/) | First edition, October 2026 |
