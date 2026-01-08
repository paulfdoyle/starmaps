# User Docs

Use this directory to build user-facing guides as PDFs. Documents here are local, PII-free by default, and intended to be generated from LaTeX sources.

## User Docs Catalog
| Document | Status | Last Updated | Files |
| --- | --- | --- | --- |
| User Guide Template | Draft | 2025-12-22 | `user_doc_template.tex` |
| Process Guide | Draft | 2025-12-22 | `process_guide.tex`, `AI_first/ui/process_guide.html` |

## How to build
1) Install a LaTeX toolchain (example: `pdflatex`).
2) From the repo root:
   ```bash
   cd AI_first/docs/user_docs
   pdflatex user_doc_template.tex
   pdflatex process_guide.tex
   ```
3) Open `user_doc_template.pdf` after it is generated.
4) The HTML version of the process guide lives at `AI_first/ui/process_guide.html`.

## Formatting and update guidance
- Keep tone and terminology consistent with `AI_first/docs/process.md` and project summaries.
- Update the catalog table when you add or publish documents.
- Record revision dates in the document header and reflect them in the catalog.
