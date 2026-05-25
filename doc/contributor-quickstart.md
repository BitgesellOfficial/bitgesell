# Bitgesell Contributor Quickstart

This guide gives new contributors a short path from a fresh fork to a focused
pull request. It is meant for small fixes, test updates, documentation changes,
and bounty submissions.

## 1. Prepare a Fork

```bash
git clone https://github.com/<your-name>/bitgesell.git
cd bitgesell
git remote add upstream https://github.com/BitgesellOfficial/bitgesell.git
git fetch upstream
git switch -c my-focused-change upstream/master
```

Keep each branch scoped to one topic. If you are working on a bounty, link the
bounty issue in the pull request body.

## 2. Choose the Smallest Useful Scope

Good first pull requests usually fit one of these categories:

- a failing or outdated test fixed in place
- a small refactor with no behavior change
- a stale command, link, or project-name reference corrected in documentation
- a focused build, CI, or lint improvement
- a narrowly described bug fix with a reproduction note

Avoid mixing unrelated formatting, refactors, and feature changes in the same
pull request. Review is easier when every diff hunk supports the same goal.

## 3. Run the Relevant Check

Pick the narrowest check that covers your change:

```bash
# Documentation-only changes
git diff --check

# Python functional-test framework changes
python3 test/functional/test_runner.py --help

# Autotools build, when dependencies are available
./autogen.sh
./configure
make check
```

If you cannot run a broader check locally, say which command was skipped and why
in the pull request notes.

## 4. Write a Reviewable Pull Request

Use the pull request body to answer these questions:

- What changed?
- Why is it useful for Bitgesell?
- Which issue or bounty does it address?
- Which checks did you run?
- Is a BTC, BGL, or USDT reward address needed for a bounty payout?

For bounty work, include the reward address only if you are comfortable sharing
it in the public pull request. Otherwise, say that you can provide it privately
after maintainer approval.

## 5. Keep the Branch Current

Before asking for a final review, rebase on the current upstream branch:

```bash
git fetch upstream
git rebase upstream/master
git push --force-with-lease
```

Use `--force-with-lease` instead of a plain force push so you do not overwrite
remote work that you have not fetched.
