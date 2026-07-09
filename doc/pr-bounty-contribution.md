# Pull Request Bounty Contribution Guide

This guide is for contributors joining Bitgesell through the pull request bounty
program. It summarizes low-risk ways to prepare useful pull requests that are
easy for maintainers to review.

## Good first bounty candidates

- Fix one failing test group or one clearly scoped test file.
- Improve build or developer documentation when the current instructions are
  incomplete, outdated, or hard to follow.
- Remove unused or obsolete code only when the behavior is clearly covered by
  existing tests or documentation.
- Refactor a small function or module without changing behavior.
- Add comments where the code is difficult to understand and the comment
  explains intent, invariants, or consensus-sensitive behavior.

## Before opening a pull request

1. Keep the change small and focused on one topic.
2. Explain why the change is useful for Bitgesell, not only that it works.
3. Run the narrowest relevant test or lint command you can run locally.
4. Mention any test you could not run and why.
5. Avoid mixing formatting-only edits with logic changes.

## Pull request checklist

- The title describes the change in one sentence.
- The description links to the bounty issue when relevant.
- The change does not introduce unrelated refactors.
- The review surface is small enough for maintainers to inspect quickly.
- Any behavior change includes a test or a clear explanation.

## Suggested pull request description

```text
Summary:
- ...

Tests:
- ...

Bounty:
- Related to PR bounty hunt issue #39.
```

## Notes for documentation-only pull requests

Documentation-only pull requests should still be substantial enough to help a
new contributor or user. Prefer adding missing instructions, clarifying build or
test steps, or documenting contributor workflow over simple typo-only changes.
