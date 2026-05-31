# Contributor Quickstart

This quickstart is for small, review-friendly pull requests, especially doc and test fixes.

## 1) Set up a branch

```bash
git checkout -b docs/contributor-quickstart
```

## 2) Keep changes scoped

- One topic per PR (docs-only, test-only, or one bug fix).
- Avoid mixing formatting churn with functional changes.
- Keep filenames and commit message clear and searchable.

## 3) Minimal validation before opening PR

For docs-only PRs:

- Verify links and paths resolve.
- Verify Markdown renders correctly.
- Run a spelling/typo pass on changed sections.

For code/test PRs:

- Run the smallest relevant local test target first.
- Include exact commands and results in PR description.

## 4) PR description template

Use this shape:

1. **What changed**
2. **Why this change is needed**
3. **How it was validated**
4. **Risk / rollback notes** (if any)

## 5) Good first PR candidates

- Clarify outdated docs and onboarding instructions.
- Fix dead links or path typos.
- Improve test/docs comments that reduce reviewer ambiguity.

Small, well-justified PRs generally review faster than broad refactors.

## 6) Common pitfalls to avoid

- Do not combine unrelated fixes in one PR.
- Do not include generated or local-environment files by accident.
- Do not force-push repeatedly after review starts unless strictly necessary.
- Do not leave validation claims without exact command output.

## 7) Final pre-push checklist

1. Re-read changed files once for clarity and typos.
2. Re-run the smallest relevant validation command.
3. Confirm `git status` only shows intended files.
4. Ensure PR description includes validation and rollback note.
