#!/usr/bin/env python3
# Copyright (c) 2020-2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test coinstatsindex across nodes.

Test that the values returned by gettxoutsetinfo are consistent
between a node running the coinstatsindex and a node without
the index.
"""

from decimal import Decimal

from test_framework.blocktools import (
    COINBASE_MATURITY,
    create_block,
    create_coinbase,
)
from test_framework.messages import (
    COIN,
    COutPoint,
    CTransaction,
    CTxIn,
    CTxOut,
)
from test_framework.script import (
    CScript,
    OP_FALSE,
    OP_RETURN,
)
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)

class CoinStatsIndexTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2
        self.supports_cli = False
        self.extra_args = [
            # Explicitly set the output type in order to have consistent tx vsize / fees
            # for both legacy and descriptor wallets (disables the change address type detection algorithm)
            ["-addresstype=bech32", "-changetype=bech32"],
            ["-coinstatsindex"]
        ]

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def run_test(self):
        self._test_coin_stats_index()
        self._test_use_index_option()
        self._test_reorg_index()
        self._test_index_rejects_hash_serialized()

    def block_sanity_check(self, block_info):
        block_subsidy = 50
        assert_equal(
            block_info['prevout_spent'] + block_subsidy,
            block_info['new_outputs_ex_coinbase'] + block_info['coinbase'] + block_info['unspendable']
        )

    def _test_coin_stats_index(self):
        node = self.nodes[0]
        index_node = self.nodes[1]
        # Both none and muhash options allow the usage of the index
        index_hash_options = ['none', 'muhash']

        # Generate a normal transaction and mine it
        self.generate(node, COINBASE_MATURITY + 1)
        address = self.nodes[0].get_deterministic_priv_key().address
        node.sendtoaddress(address=address, amount=10, subtractfeefromamount=True)
        self.generate(node, 1)

        self.log.info("Test that gettxoutsetinfo() output is consistent with or without coinstatsindex option")
        res0 = node.gettxoutsetinfo('none')

        # The fields 'disk_size' and 'transactions' do not exist on the index
        del res0['disk_size'], res0['transactions']

        for hash_option in index_hash_options:
            res1 = index_node.gettxoutsetinfo(hash_option)
            # The fields 'block_info' and 'total_unspendable_amount' only exist on the index
            del res1['block_info'], res1['total_unspendable_amount']
            res1.pop('muhash', None)

            # Everything left should be the same
            assert_equal(res1, res0)

        self.log.info("Test that gettxoutsetinfo() can get fetch data on specific heights with index")

        # Generate a new tip
        self.generate(node, 5)

        for hash_option in index_hash_options:
            # Fetch old stats by height
            res2 = index_node.gettxoutsetinfo(hash_option, 102)
            del res2['block_info'], res2['total_unspendable_amount']
            res2.pop('muhash', None)
            assert_equal(res0, res2)

            # Fetch old stats by hash
            res3 = index_node.gettxoutsetinfo(hash_option, res0['bestblock'])
            del res3['block_info'], res3['total_unspendable_amount']
            res3.pop('muhash', None)
            assert_equal(res0, res3)

            # It does not work without coinstatsindex
            assert_raises_rpc_error(-8, "Querying specific block heights requires coinstatsindex", node.gettxoutsetinfo, hash_option, 102)

        self.log.info("Test gettxoutsetinfo() with index and verbose flag")

        for hash_option in index_hash_options:
            # Genesis block is unspendable
            res4 = index_node.gettxoutsetinfo(hash_option, 0)
            assert_equal(res4['total_unspendable_amount'], 50)
            assert_equal(res4['block_info'], {
                'unspendable': 50,
                'prevout_spent': 0,
                'new_outputs_ex_coinbase': 0,
                'coinbase': 0,
                'unspendables': {
                    'genesis_block': 50,
                    'bip30': 0,
                    'scripts': 0,
                    'unclaimed_rewards': 0
                }
            })
            self.block_sanity_check(res4['block_info'])

            # Test an older block height that included a normal tx
            res5 = index_node.gettxoutsetinfo(hash_option, 102)
            assert_equal(res5['total_unspendable_amount'], 50)
            assert_equal(res5['block_info'], {
                'unspendable': 0,
                'prevout_spent': 50,
                'new_outputs_ex_coinbase': Decimal('49.99995560'),
                'coinbase': Decimal('50.00004440'),
                'unspendables': {
                    'genesis_block': 0,
                    'bip30': 0,
                    'scripts': 0,
                    'unclaimed_rewards': 0
                }
            })
            self.block_sanity_check(res5['block_info'])

        # Generate and send a normal tx with two outputs
        tx1_inputs = []
        tx1_outputs = {self.nodes[0].getnewaddress(): 21, self.nodes[0].getnewaddress(): 42}
        raw_tx1 = self.nodes[0].createrawtransaction(tx1_inputs, tx1_outputs)
        funded_tx1 = self.nodes[0].fundrawtransaction(raw_tx1)
        signed_tx1 = self.nodes[0].signrawtransactionwithwallet(funded_tx1['hex'])
        tx1_txid = self.nodes[0].sendrawtransaction(signed_tx1['hex'])

        # Find the right position of the 21 BTC output
        tx1_final = self.nodes[0].gettransaction(tx1_txid)
        for output in tx1_final['details']:
            if output['amount'] == Decimal('21.00000000') and output['category'] == 'receive':
                n = output['vout']

        # Generate and send another tx with an OP_RETURN output (which is unspendable)
        tx2 = CTransaction()
        tx2.vin.append(CTxIn(COutPoint(int(tx1_txid, 16), n), b''))
        tx2.vout.append(CTxOut(int(Decimal('20.99') * COIN), CScript([OP_RETURN] + [OP_FALSE]*30)))
        tx2_hex = self.nodes[0].signrawtransactionwithwallet(tx2.serialize().hex())['hex']
        self.nodes[0].sendrawtransaction(tx2_hex)

        # Include both txs in a block
        self.generate(self.nodes[0], 1)

        for hash_option in index_hash_options:
            # Check all amounts were registered correctly
            res6 = index_node.gettxoutsetinfo(hash_option, 108)
            assert_equal(res6['total_unspendable_amount'], Decimal('70.99000000'))
            assert_equal(res6['block_info'], {
                'unspendable': Decimal('20.99000000'),
                'prevout_spent': 111,
                'new_outputs_ex_coinbase': Decimal('89.99993620'),
                'coinbase': Decimal('50.01006380'),
                'unspendables': {
                    'genesis_block': 0,
                    'bip30': 0,
                    'scripts': Decimal('20.99000000'),
                    'unclaimed_rewards': 0
                }
            })
            self.block_sanity_check(res6['block_info'])

        # Create a coinbase that does not claim full subsidy and also
        # has two outputs
        cb = create_coinbase(109, nValue=35)
        cb.vout.append(CTxOut(5 * COIN, CScript([OP_FALSE])))
        cb.rehash()

        # Generate a block that includes previous coinbase
        tip = self.nodes[0].getbestblockhash()
        block_time = self.nodes[0].getblock(tip)['time'] + 1
        block = create_block(int(tip, 16), cb, block_time)
        block.solve()
        self.nodes[0].submitblock(block.serialize().hex())
        self.sync_all()

        for hash_option in index_hash_options:
            res7 = index_node.gettxoutsetinfo(hash_option, 109)
            assert_equal(res7['total_unspendable_amount'], Decimal('80.99000000'))
            assert_equal(res7['block_info'], {
                'unspendable': 10,
                'prevout_spent': 0,
                'new_outputs_ex_coinbase': 0,
                'coinbase': 40,
                'unspendables': {
                    'genesis_block': 0,
                    'bip30': 0,
                    'scripts': 0,
                    'unclaimed_rewards': 10
                }
            })
            self.block_sanity_check(res7['block_info'])

        self.log.info("Test that the index is robust across restarts")

        res8 = index_node.gettxoutsetinfo('muhash')
        self.restart_node(1, extra_args=self.extra_args[1])
        res9 = index_node.gettxoutsetinfo('muhash')
        assert_equal(res8, res9)

        self.generate(index_node, 1, sync_fun=self.no_op)
        res10 = index_node.gettxoutsetinfo('muhash')
        assert(res8['txouts'] < res10['txouts'])

    def _test_use_index_option(self):
        self.log.info("Test use_index option for nodes running the index")

        self.connect_nodes(0, 1)
        self.nodes[0].waitforblockheight(110)
        res = self.nodes[0].gettxoutsetinfo('muhash')
        option_res = self.nodes[1].gettxoutsetinfo(hash_type='muhash', hash_or_height=None, use_index=False)
        del res['disk_size'], option_res['disk_size']
        assert_equal(res, option_res)

    def _test_reorg_index(self):
        self.log.info("Test that index can handle reorgs")

        # Generate two block, let the index catch up, then invalidate the blocks
        index_node = self.nodes[1]
        reorg_blocks = self.generatetoaddress(index_node, 2, index_node.getnewaddress())
        reorg_block = reorg_blocks[1]
        res_invalid = index_node.gettxoutsetinfo('muhash')
        index_node.invalidateblock(reorg_blocks[0])
        assert_equal(index_node.gettxoutsetinfo('muhash')['height'], 110)

        # Add two new blocks
        block = self.generate(index_node, 2, sync_fun=self.no_op)[1]
        res = index_node.gettxoutsetinfo(hash_type='muhash', hash_or_height=None, use_index=False)

        # Test that the result of the reorged block is not returned for its old block height
        res2 = index_node.gettxoutsetinfo(hash_type='muhash', hash_or_height=112)
        assert_equal(res["bestblock"], block)
        assert_equal(res["muhash"], res2["muhash"])
        assert(res["muhash"] != res_invalid["muhash"])

        # Test that requesting reorged out block by hash is still returning correct results
        res_invalid2 = index_node.gettxoutsetinfo(hash_type='muhash', hash_or_height=reorg_block)
        assert_equal(res_invalid2["muhash"], res_invalid["muhash"])
        assert(res["muhash"] != res_invalid2["muhash"])

        # Add another block, so we don't depend on reconsiderblock remembering which
        # blocks were touched by invalidateblock
        self.generate(index_node, 1)

        # Ensure that removing and re-adding blocks yields consistent results
        block = index_node.getblockhash(99)
        index_node.invalidateblock(block)
        index_node.reconsiderblock(block)
        res3 = index_node.gettxoutsetinfo(hash_type='muhash', hash_or_height=112)
        assert_equal(res2, res3)

    def _test_index_rejects_hash_serialized(self):
        self.log.info("Test that the rpc raises if the legacy hash is passed with the index")

        msg = "hash_serialized_2 hash type cannot be queried for a specific block"
        assert_raises_rpc_error(-8, msg, self.nodes[1].gettxoutsetinfo, hash_type='hash_serialized_2', hash_or_height=111)

        for use_index in {True, False, None}:
            assert_raises_rpc_error(-8, msg, self.nodes[1].gettxoutsetinfo, hash_type='hash_serialized_2', hash_or_height=111, use_index=use_index)


if __name__ == '__main__':
    CoinStatsIndexTest().main()
