### The task of syncing the code

To sync code of BGL (which was based, but not forked) to BTC code base.
It is unclear if the full compatibility regarding RPC and code would stay, but
for now it is the case. Original change history is not present, so the procedure would include batch picking of commits to include.

- we are syncing with the bitcoin master branch;
- all merge commits are skipped (merge commits can include commits from long ago and those already processed, processing them would be very non-linear and complicated), picking all non-merge commits will result in the changes coming the same way as they are present in the bitcoin master branch;

The log of sync is kept in file sync_log.txt in this folder.

### Flow of making synchronization

- Check out latest BGL repo, the commits would go to `bitcoinsync` branch;
- Add bitcoin main repository as remote and fetch it:
   ```
   git remote add btcrepo https://github.com/bitcoin/bitcoin/
   git fetch btcrepo
   ```
- Get the list of commits to process (for example, from current point of 31st of March):
   ```
   git log btcrepo/master --pretty=format:'%cd %H %s' --since="2020-03-31" --date=iso-local | sort -r
   ```
   (it will sort them in the order of them being merged)
- While switched to `bitcoinsync` branch, start cherry-picking commits in chronological order one by one
   ```
   git cherry-pick <commit-hash>
   ```
- if a commit is a PR merged (merge commit), having Merge #number in the name, skip it;

There could be several possible outcomes:
- Commit merges cleanly:
  - make the mark that it had been processed and move to the next;
- Commit has merge conflicts:
  - check that commit is not for the submodule (such as leveldb), otherwise, skip it;
  - resolve conflicts:
    - mostly accept all incoming changes;
    - in the incoming changes rename bitcoin to BGL where applicable in class names, etc.;
    - check also section below 'Changes to keep';
  - when conflicts resolved, merge cherry-pick as
    ```git add -A && git commit```
  - mark that commit had been processed and move to the next;
- Commit has zero changes
  - it should occur pretty rarely, mostly when such file has already been deleted;
  - make empty commit with
    ```git commit --allow-empty```
  - make the mark that commit had been processed and move to the next;

After a chunk of commits had been processed, before pushing the changes:
- Search for `bitcoin` in source files and perform checks/replaces where needed;
- Check for compilation and running from scratch (from autogen to running `BGLd` executable);
- if some files got damaged or broken, get them from BTC repository and perform replacements
  (use file version for the proper commit state on which the process is now);
- Commit any changes if present too;

### Notes and possible pitfalls

- File renames are usually picked up nicely, but some files with 'bitcoin' in the name are renamed
  to 'BGL' in the name, and may have to be manually moved/renamed;
  - file renames that are not detected;
  - file moves in folder tree that are not detected (rare case, occurence wasn't observed);
- The ordering of the commits, merged to bitcoin master branch in the same second may be wrong, 
  if first cannot me auto-merged cleanly, check the second one;

- Merge commits are skipped
  - even if merge conflicts would be before merging a PR, conflict resolve is a separate commit
  - squash-commits would be as a single commit (not merge commit)
  - we are tracking master branch from a point in time, when PRs are merged they contain single commits (in appropriate times),
    so if we merging all of them, the code should follow the original master branch

### Changes to keep

Remember to keep changes related to:
- burning of tx fees;
- chain parameters (most of the chainparams.cpp);
- hashing of block or transaction (sha3-keccak);
	e.g. to avoid ambiguity, the function name explicitly stating the hash is used:
	`SerializeHash` -> `SerializeHashSHA256` or `SerializeHashKeccak`
- naming (BGL);

Important files:
- chainparams.cpp
- validation.cpp
- hash.cpp
- consensus.h (block size)

### Useful tools

Very convenient to use not only regular textual, but also 2-panel graphical diff (Meld, Windiff, etc.), especially after larger commits or after a chunk has been processed before test build of the resulted code.

### Current status

All commits are merged from Dec 2019 up to 31 March 2020 (around 30% of all commits that BGL is behind BTC). Additional commit is created to close some of the changes that were not included (e.g. due to being present in
merge commit with changes earlier than those from 15 Dec 2019, there are changes year and more earlier).
We would sync those with re-checking the files and there should be less of those when moving forward with the task.
The BGL binaries were successfully built (except Qt wallet, it could be checked after all other commits synced) and node checked to be running and syncing.

### Completion

After all the changes are synced, we should check tests state, check node and wallet functions, diff files significantly changing in size and fix discrepancies found. Properly integrate submodules (leveldb, etc.)

In addition, areas of interest would be Windows/Mac versions, and overall packaging, as the next step would be provision of automated builds (and pipeline/tooling may differ from used in BTC).

