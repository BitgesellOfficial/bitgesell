#!/usr/bin/env python3
# Copyright (c) 2019-2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the generation of UTXO snapshots using `dumptxoutset`.
"""
from pathlib import Path

from test_framework.blocktools import COINBASE_MATURITY
from test_framework.test_framework import BGLTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
    sha256sum_file,
)


class DumptxoutsetTest(BGLTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1

    def run_test(self):
        """Test a trivial usage of the dumptxoutset RPC command."""
        node = self.nodes[0]
        mocktime = node.getblockheader(node.getblockhash(0))['time'] + 1
        node.setmocktime(mocktime)
        self.generate(node, COINBASE_MATURITY)

        FILENAME = 'txoutset.dat'
        out = node.dumptxoutset(FILENAME)
        expected_path = Path(node.datadir) / self.chain / FILENAME

        assert expected_path.is_file()

        assert_equal(out['coins_written'], 100)
        assert_equal(out['base_height'], 100)
        assert_equal(out['path'], str(expected_path))
        # Blockhash should be deterministic based on mocked time.
        assert_equal(
            out['base_hash'],
            '579688e1c37db76fb91df0e1cd876b8885bef8cd266a3fef25ea3227c7e28209')

        # UTXO snapshot hash should be deterministic based on mocked time.
        assert_equal(
            sha256sum_file(str(expected_path)).hex(),
            'bb5a2be762988a5d08c787c82e1e782efb6cf1a0544e95dbcb1cab338e510c8b')

        assert_equal(
            out['txoutset_hash'], '1f1493bf052e2c0fdd637c2fa3067bc2b36df0a6a9deffda60cf5d9698f990e6')
        assert_equal(out['nchaintx'], 101)

        # Specifying a path to an existing or invalid file will fail.
        assert_raises_rpc_error(
            -8, '{} already exists'.format(FILENAME),  node.dumptxoutset, FILENAME)
        invalid_path = node.datadir_path / "invalid" / "path"
        assert_raises_rpc_error(
            -8, "Couldn't open file {}.incomplete for writing".format(invalid_path), node.dumptxoutset, invalid_path)


if __name__ == '__main__':
    DumptxoutsetTest().main()
