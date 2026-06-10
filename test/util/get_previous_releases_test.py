#!/usr/bin/env python3
#
# Copyright (c) 2026 The Bitgesell Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Unit tests for test/get_previous_releases.py helpers."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / 'get_previous_releases.py'
SPEC = importlib.util.spec_from_file_location('get_previous_releases', SCRIPT_PATH)
get_previous_releases = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(get_previous_releases)


class GetPreviousReleasesTest(unittest.TestCase):
    def test_normalizes_bitcoin_binary_names_to_bgl_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bin_path = Path(tmpdir)
            for old_name in get_previous_releases.PREVIOUS_RELEASE_BINARY_RENAMES:
                (bin_path / old_name).write_text('binary placeholder', encoding='utf8')

            get_previous_releases.normalize_previous_release_binary_names(bin_path)

            for old_name, new_name in get_previous_releases.PREVIOUS_RELEASE_BINARY_RENAMES.items():
                self.assertFalse((bin_path / old_name).exists())
                self.assertEqual((bin_path / new_name).read_text(encoding='utf8'), 'binary placeholder')

    def test_does_not_overwrite_existing_bgl_binary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bin_path = Path(tmpdir)
            (bin_path / 'bitcoind').write_text('old binary', encoding='utf8')
            (bin_path / 'BGLd').write_text('new binary', encoding='utf8')

            get_previous_releases.normalize_previous_release_binary_names(bin_path)

            self.assertEqual((bin_path / 'BGLd').read_text(encoding='utf8'), 'new binary')
            self.assertEqual((bin_path / 'bitcoind').read_text(encoding='utf8'), 'old binary')


if __name__ == '__main__':
    unittest.main()
