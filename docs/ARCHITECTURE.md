# Architecture

```text
React + Vite frontend
        |
        | HTTP multipart / JSON
        v
FastAPI (/api)
  ├── /analyze       -> OCR -> ELA + metadata + QR -> risk summary
  ├── /identity-check -> cross-document field comparison
  ├── /risk-score     -> standalone risk calculation
  └── /report         -> PDF generation + download
```

The combined screening endpoint saves the uploaded image with a generated filename, so the original user-supplied filename is never used as a filesystem path. Uploads and generated PDFs are runtime data and are excluded from Git.

The risk score is a hand-designed heuristic for a demo, not a trained or calibrated model. Face verification is not implemented in this repository snapshot. Human review and trusted external checks remain necessary.
