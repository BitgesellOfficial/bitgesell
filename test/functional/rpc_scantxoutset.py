#!/usr/bin/env python3
# Copyright (c) 2018-2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the scantxoutset rpc call."""
from test_framework.test_framework import BGLTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error

from decimal import Decimal
import shutil
import os

def descriptors(out):
    return sorted(u['desc'] for u in out['unspents'])

class ScantxoutsetTest(BGLTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def run_test(self):
        self.log.info("Mining blocks...")
        self.generate(self.nodes[0], 110)

        addr_P2SH_SEGWIT = self.nodes[0].getnewaddress("", "p2sh-segwit")
        pubk1 = self.nodes[0].getaddressinfo(addr_P2SH_SEGWIT)['pubkey']
        addr_LEGACY = self.nodes[0].getnewaddress("", "legacy")
        pubk2 = self.nodes[0].getaddressinfo(addr_LEGACY)['pubkey']
        addr_BECH32 = self.nodes[0].getnewaddress("", "bech32")
        pubk3 = self.nodes[0].getaddressinfo(addr_BECH32)['pubkey']
        self.nodes[0].sendtoaddress(addr_P2SH_SEGWIT, 0.001)
        self.nodes[0].sendtoaddress(addr_LEGACY, 0.002)
        self.nodes[0].sendtoaddress(addr_BECH32, 0.004)

        #send to child keys of tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK
        self.nodes[0].sendtoaddress("rbgl1qx3x8pd2j82774x9v5jtrt67v6eq0xg33h9wtfn", 0.008) # (m/0'/0'/0')
        self.nodes[0].sendtoaddress("rbgl1qysufe22kf66mz3jtq33f0d88arruws4ye5egv0", 0.016) # (m/0'/0'/1')
        self.nodes[0].sendtoaddress("rbgl1qan5n5jj47futj90060396taeegswnhusutx05j", 0.032) # (m/0'/0'/1500')

        self.nodes[0].sendtoaddress("rbgl1qdny83c9q5x3glq86aa68gevelzqwwu9qhdhxqa", 0.064) # (m/0'/0'/0)
        self.nodes[0].sendtoaddress("rbgl1qfs4pjvfdkscn82qraqvvwahw0fyd20ykgp4hjd", 0.128) # (m/0'/0'/1)
        self.nodes[0].sendtoaddress("rbgl1q8pvg59ekgx6lryuysvqf4ljtgyjr8nsl3kl00s", 0.256) # (m/0'/0'/1500)

        self.nodes[0].sendtoaddress("rbgl1qy7u0mmtl4qz4833p8f43v63m7nqmscls6jgxc8", 0.512) # (m/1/1/0')
        self.nodes[0].sendtoaddress("rbgl1qqt5rga2600fjzhlvh89p8qy7nyrp9e6807hwha", 1.024) # (m/1/1/1')
        self.nodes[0].sendtoaddress("rbgl1qt0c33ft6cfw852p6chqvqpkwxvmfl8vnzy02zv", 2.048) # (m/1/1/1500')

        self.nodes[0].sendtoaddress("rbgl1qjqmxmkpmxt80xz4y3746zgt0q3u3ferrg2ss57", 4.096) # (m/1/1/0)
        self.nodes[0].sendtoaddress("rbgl1qhku5rq7jz8ulufe2y6fkcpnlvpsta7rqv2cz5w", 8.192) # (m/1/1/1)
        self.nodes[0].sendtoaddress("rbgl1qv9hs5rhkgcx0ef6f9g26k3k83hmhugjtart6dr", 16.384) # (m/1/1/1500)


        self.generate(self.nodes[0], 1)

        self.log.info("Stop node, remove wallet, mine again some blocks...")
        self.stop_node(0)
        shutil.rmtree(os.path.join(self.nodes[0].datadir, self.chain, 'wallets'))
        self.start_node(0, ['-nowallet'])
        self.import_deterministic_coinbase_privkeys()
        self.generate(self.nodes[0], 110)

        scan = self.nodes[0].scantxoutset("start", [])
        info = self.nodes[0].gettxoutsetinfo()
        assert_equal(scan['success'], True)
        assert_equal(scan['height'], info['height'])
        assert_equal(scan['txouts'], info['txouts'])
        assert_equal(scan['bestblock'], info['bestblock'])

        self.restart_node(0, ['-nowallet'])
        self.log.info("Test if we have found the non HD unspent outputs.")
        assert_equal(self.nodes[0].scantxoutset("start", [ "pkh(" + pubk1 + ")", "pkh(" + pubk2 + ")", "pkh(" + pubk3 + ")"])['total_amount'], Decimal("0.002"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "wpkh(" + pubk1 + ")", "wpkh(" + pubk2 + ")", "wpkh(" + pubk3 + ")"])['total_amount'], Decimal("0.004"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "sh(wpkh(" + pubk1 + "))", "sh(wpkh(" + pubk2 + "))", "sh(wpkh(" + pubk3 + "))"])['total_amount'], Decimal("0.001"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(" + pubk1 + ")", "combo(" + pubk2 + ")", "combo(" + pubk3 + ")"])['total_amount'], Decimal("0.007"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "addr(" + addr_P2SH_SEGWIT + ")", "addr(" + addr_LEGACY + ")", "addr(" + addr_BECH32 + ")"])['total_amount'], Decimal("0.007"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "addr(" + addr_P2SH_SEGWIT + ")", "addr(" + addr_LEGACY + ")", "combo(" + pubk3 + ")"])['total_amount'], Decimal("0.007"))

        self.log.info("Test range validation.")
        assert_raises_rpc_error(-8, "End of range is too high", self.nodes[0].scantxoutset, "start", [ {"desc": "desc", "range": -1}])
        assert_raises_rpc_error(-8, "Range should be greater or equal than 0", self.nodes[0].scantxoutset, "start", [ {"desc": "desc", "range": [-1, 10]}])
        assert_raises_rpc_error(-8, "End of range is too high", self.nodes[0].scantxoutset, "start", [ {"desc": "desc", "range": [(2 << 31 + 1) - 1000000, (2 << 31 + 1)]}])
        assert_raises_rpc_error(-8, "Range specified as [begin,end] must not have begin after end", self.nodes[0].scantxoutset, "start", [ {"desc": "desc", "range": [2, 1]}])
        assert_raises_rpc_error(-8, "Range is too large", self.nodes[0].scantxoutset, "start", [ {"desc": "desc", "range": [0, 1000001]}])

        self.log.info("Test extended key derivation.")
        # Run various scans, and verify that the sum of the amounts of the matches corresponds to the expected subset.
        # Note that all amounts in the UTXO set are powers of 2 multiplied by 0.001 BGL, so each amounts uniquely identifies a subset.
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0'/0h/0h)"])['total_amount'], Decimal("0.008"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0'/0'/1h)"])['total_amount'], Decimal("0.016"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0h/0'/1500')"])['total_amount'], Decimal("0.032"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0h/0h/0)"])['total_amount'], Decimal("0.064"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0'/0h/1)"])['total_amount'], Decimal("0.128"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0h/0'/1500)"])['total_amount'], Decimal("0.256"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0'/0h/*h)", "range": 1499}])['total_amount'], Decimal("0.024"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0'/0'/*h)", "range": 1500}])['total_amount'], Decimal("0.056"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0h/0'/*)", "range": 1499}])['total_amount'], Decimal("0.192"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0'/0h/*)", "range": 1500}])['total_amount'], Decimal("0.448"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/0')"])['total_amount'], Decimal("0.512"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/1')"])['total_amount'], Decimal("1.024"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/1500h)"])['total_amount'], Decimal("2.048"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/0)"])['total_amount'], Decimal("4.096"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/1)"])['total_amount'], Decimal("8.192"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/1500)"])['total_amount'], Decimal("16.384"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1/1/0)"])['total_amount'], Decimal("4.096"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo([abcdef88/1/2'/3/4h]tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1/1/1)"])['total_amount'], Decimal("8.192"))
        assert_equal(self.nodes[0].scantxoutset("start", [ "combo(tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1/1/1500)"])['total_amount'], Decimal("16.384"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/*')", "range": 1499}])['total_amount'], Decimal("1.536"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/*')", "range": 1500}])['total_amount'], Decimal("3.584"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/*)", "range": 1499}])['total_amount'], Decimal("12.288"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/*)", "range": 1500}])['total_amount'], Decimal("28.672"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1/1/*)", "range": 1499}])['total_amount'], Decimal("12.288"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1/1/*)", "range": 1500}])['total_amount'], Decimal("28.672"))
        assert_equal(self.nodes[0].scantxoutset("start", [ {"desc": "combo(tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1/1/*)", "range": [1500,1500]}])['total_amount'], Decimal("16.384"))


        # Check that status and abort don't need second arg
        assert_equal(self.nodes[0].scantxoutset("status"), None)
        assert_equal(self.nodes[0].scantxoutset("abort"), False)

        # Check that second arg is needed for start
        assert_raises_rpc_error(-1, "scanobjects argument is required for the start action", self.nodes[0].scantxoutset, "start")

if __name__ == '__main__':
    ScantxoutsetTest().main()
