This folder contains lint scripts.

Running locally
===============

To run linters locally with the same versions as the CI environment, use the included
Dockerfile:

```sh
DOCKER_BUILDKIT=1 docker build -t bitcoin-linter --file "./ci/lint_imagefile" ./

docker run --rm -v $(pwd):/bitcoin -it bitcoin-linter
```

After building the container once, you can simply run the last command any time you
want to lint.

test runner
===========

To run all the lint checks in the test runner outside the docker, use:

```sh
( cd ./test/lint/test_runner/ && cargo fmt && cargo clippy && RUST_BACKTRACE=1 cargo run )
```

#### Dependencies

| Lint test | Dependency |
|-----------|:----------:|
| [`lint-python.py`](lint/lint-python.py) | [flake8](https://gitlab.com/pycqa/flake8)
| [`lint-python.py`](lint/lint-python.py) | [lief](https://github.com/lief-project/LIEF)
| [`lint-python.py`](lint/lint-python.py) | [mypy](https://github.com/python/mypy)
| [`lint-python.py`](lint/lint-python.py) | [pyzmq](https://github.com/zeromq/pyzmq)
| [`lint-python-dead-code.py`](lint/lint-python-dead-code.py) | [vulture](https://github.com/jendrikseipp/vulture)
| [`lint-shell.py`](lint/lint-shell.py) | [ShellCheck](https://github.com/koalaman/shellcheck)
| [`lint-spelling.py`](lint/lint-spelling.py) | [codespell](https://github.com/codespell-project/codespell)

In use versions and install instructions are available in the [CI setup](../../ci/lint/04_install.sh).

Please be aware that on Linux distributions all dependencies are usually available as packages, but could be outdated.

#### Running the tests

Individual tests can be run by directly calling the test script, e.g.:

```
test/lint/lint-files.py
```

check-doc.py
============
Check for missing documentation of command line options.

commit-script-check.sh
======================
Verification of [scripted diffs](/doc/developer-notes.md#scripted-diffs).
Scripted diffs are only assumed to run on the latest LTS release of Ubuntu. Running them on other operating systems
might require installing GNU tools, such as GNU sed.

git-subtree-check.sh
====================
Run this script from the root of the repository to verify that a subtree matches the contents of
the commit it claims to have been updated to.

```
Usage: test/lint/git-subtree-check.sh [-r] DIR [COMMIT]
       test/lint/git-subtree-check.sh -?
```

- `DIR` is the prefix within the repository to check.
- `COMMIT` is the commit to check, if it is not provided, HEAD will be used.
- `-r` checks that subtree commit is present in repository.

To do a full check with `-r`, make sure that you have fetched the upstream repository branch in which the subtree is
maintained:
* for `src/secp256k1`: https://github.com/bitcoin-core/secp256k1.git (branch master)
* for `src/leveldb`: https://github.com/bitcoin-core/leveldb-subtree.git (branch bitcoin-fork)
* for `src/crypto/ctaes`: https://github.com/bitcoin-core/ctaes.git (branch master)
* for `src/crc32c`: https://github.com/bitcoin-core/crc32c-subtree.git (branch bitcoin-fork)

To do so, add the upstream repository as remote:

```
git remote add --fetch secp256k1 https://github.com/bitcoin-core/secp256k1.git
```
