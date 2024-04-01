#!/usr/bin/env python3
# Copyright (c) 2014-2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test mempool limiting together/eviction with the wallet."""

from decimal import Decimal

from test_framework.blocktools import COINBASE_MATURITY
from test_framework.p2p import P2PTxInvStore
from test_framework.test_framework import BGLTestFramework
from test_framework.util import (
    assert_equal,
    assert_fee_amount,
    assert_greater_than,
    assert_raises_rpc_error,
    create_lots_of_big_transactions,
    gen_return_txouts,
)
from test_framework.wallet import (
    COIN,
    DEFAULT_FEE,
    MiniWallet,
)


class MempoolLimitTest(BGLTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1
        self.extra_args = [[
            "-datacarriersize=100000",
            "-maxmempool=5",
        ]]
        self.supports_cli = False

    def run_test(self):
        txouts = gen_return_txouts()
        node = self.nodes[0]
        miniwallet = MiniWallet(node)
        relayfee = node.getnetworkinfo()['relayfee']

        self.log.info('Check that mempoolminfee is minrelaytxfee')
        assert_equal(node.getmempoolinfo()['minrelaytxfee'], Decimal('0.00001000'))
        assert_equal(node.getmempoolinfo()['mempoolminfee'], Decimal('0.00001000'))

        tx_batch_size = 250
        num_of_batches = 3
        # Generate UTXOs to flood the mempool
        # 1 to create a tx initially that will be evicted from the mempool later
        # 3 batches of multiple transactions with a fee rate much higher than the previous UTXO
        # And 1 more to verify that this tx does not get added to the mempool with a fee rate less than the mempoolminfee
        # And 2 more for the package cpfp test
        self.generate(miniwallet, 1 + (num_of_batches * tx_batch_size) + 1 + 2)

        # Mine 99 blocks so that the UTXOs are allowed to be spent
        self.generate(node, COINBASE_MATURITY - 1)

        self.log.info('Create a mempool tx that will be evicted')

        tx_to_be_evicted_id = miniwallet.send_self_transfer(from_node=node, fee_rate=relayfee)["txid"]
        # Increase the tx fee rate to give the subsequent transactions a higher priority in the mempool
        # The tx has an approx. vsize of 65k, i.e. multiplying the previous fee rate (in sats/kvB)
        # by 130 should result in a fee that corresponds to 2x of that fee rate
        base_fee = relayfee * 130

        self.log.info("Fill up the mempool with txs with higher fee rate")
        for batch_of_txid in range(num_of_batches):
            fee = (batch_of_txid + 1) * base_fee
            create_lots_of_big_transactions(miniwallet, node, fee, tx_batch_size, txouts)

        self.log.info('The tx should be evicted by now')
        # The number of transactions created should be greater than the ones present in the mempool
        assert_greater_than(tx_batch_size * num_of_batches, len(node.getrawmempool()))
        # Initial tx created should not be present in the mempool anymore as it had a lower fee rate
        assert tx_to_be_evicted_id not in node.getrawmempool()

        self.log.info('Check that mempoolminfee is larger than minrelaytxfee')
        assert_equal(node.getmempoolinfo()['minrelaytxfee'], Decimal('0.00001000'))
        assert_greater_than(node.getmempoolinfo()['mempoolminfee'], Decimal('0.00001000'))

    def test_mid_package_eviction(self):
        node = self.nodes[0]
        self.log.info("Check a package where each parent passes the current mempoolminfee but would cause eviction before package submission terminates")

        self.restart_node(0, extra_args=self.extra_args[0])

        # Restarting the node resets mempool minimum feerate
        assert_equal(node.getmempoolinfo()['minrelaytxfee'], Decimal('0.00001000'))
        assert_equal(node.getmempoolinfo()['mempoolminfee'], Decimal('0.00001000'))

        self.fill_mempool()
        current_info = node.getmempoolinfo()
        mempoolmin_feerate = current_info["mempoolminfee"]

        package_hex = []
        # UTXOs to be spent by the ultimate child transaction
        parent_utxos = []

        evicted_weight = 8000
        # Mempool transaction which is evicted due to being at the "bottom" of the mempool when the
        # mempool overflows and evicts by descendant score. It's important that the eviction doesn't
        # happen in the middle of package evaluation, as it can invalidate the coins cache.
        mempool_evicted_tx = self.wallet.send_self_transfer(
            from_node=node,
            fee=(mempoolmin_feerate / 1000) * (evicted_weight // 4) + Decimal('0.000001'),
            target_weight=evicted_weight,
            confirmed_only=True
        )
        # Already in mempool when package is submitted.
        assert mempool_evicted_tx["txid"] in node.getrawmempool()

        # This parent spends the above mempool transaction that exists when its inputs are first
        # looked up, but disappears later. It is rejected for being too low fee (but eligible for
        # reconsideration), and its inputs are cached. When the mempool transaction is evicted, its
        # coin is no longer available, but the cache could still contains the tx.
        cpfp_parent = self.wallet.create_self_transfer(
            utxo_to_spend=mempool_evicted_tx["new_utxo"],
            fee_rate=mempoolmin_feerate - Decimal('0.00001'),
            confirmed_only=True)
        package_hex.append(cpfp_parent["hex"])
        parent_utxos.append(cpfp_parent["new_utxo"])
        assert_equal(node.testmempoolaccept([cpfp_parent["hex"]])[0]["reject-reason"], "mempool min fee not met")

        self.wallet.rescan_utxos()

        # Series of parents that don't need CPFP and are submitted individually. Each one is large and
        # high feerate, which means they should trigger eviction but not be evicted.
        parent_weight = 100000
        num_big_parents = 3
        assert_greater_than(parent_weight * num_big_parents, current_info["maxmempool"] - current_info["bytes"])
        parent_fee = (100 * mempoolmin_feerate / 1000) * (parent_weight // 4)

        big_parent_txids = []
        for i in range(num_big_parents):
            parent = self.wallet.create_self_transfer(fee=parent_fee, target_weight=parent_weight, confirmed_only=True)
            parent_utxos.append(parent["new_utxo"])
            package_hex.append(parent["hex"])
            big_parent_txids.append(parent["txid"])
            # There is room for each of these transactions independently
            assert node.testmempoolaccept([parent["hex"]])[0]["allowed"]

        # Create a child spending everything, bumping cpfp_parent just above mempool minimum
        # feerate. It's important not to bump too much as otherwise mempool_evicted_tx would not be
        # evicted, making this test much less meaningful.
        approx_child_vsize = self.wallet.create_self_transfer_multi(utxos_to_spend=parent_utxos)["tx"].get_vsize()
        cpfp_fee = (mempoolmin_feerate / 1000) * (cpfp_parent["tx"].get_vsize() + approx_child_vsize) - cpfp_parent["fee"]
        # Specific number of satoshis to fit within a small window. The parent_cpfp + child package needs to be
        # - When there is mid-package eviction, high enough feerate to meet the new mempoolminfee
        # - When there is no mid-package eviction, low enough feerate to be evicted immediately after submission.
        magic_satoshis = 1200
        cpfp_satoshis = int(cpfp_fee * COIN) + magic_satoshis

        child = self.wallet.create_self_transfer_multi(utxos_to_spend=parent_utxos, fee_per_output=cpfp_satoshis)
        package_hex.append(child["hex"])

        # Package should be submitted, temporarily exceeding maxmempool, and then evicted.
        with node.assert_debug_log(expected_msgs=["rolling minimum fee bumped"]):
            assert_raises_rpc_error(-26, "mempool full", node.submitpackage, package_hex)

        # Maximum size must never be exceeded.
        assert_greater_than(node.getmempoolinfo()["maxmempool"], node.getmempoolinfo()["bytes"])

        # Evicted transaction and its descendants must not be in mempool.
        resulting_mempool_txids = node.getrawmempool()
        assert mempool_evicted_tx["txid"] not in resulting_mempool_txids
        assert cpfp_parent["txid"] not in resulting_mempool_txids
        assert child["txid"] not in resulting_mempool_txids
        for txid in big_parent_txids:
            assert txid in resulting_mempool_txids

    def test_mid_package_replacement(self):
        node = self.nodes[0]
        self.log.info("Check a package where an early tx depends on a later-replaced mempool tx")

        self.restart_node(0, extra_args=self.extra_args[0])

        # Restarting the node resets mempool minimum feerate
        assert_equal(node.getmempoolinfo()['minrelaytxfee'], Decimal('0.00001000'))
        assert_equal(node.getmempoolinfo()['mempoolminfee'], Decimal('0.00001000'))

        self.fill_mempool()
        current_info = node.getmempoolinfo()
        mempoolmin_feerate = current_info["mempoolminfee"]

        # Mempool transaction which is evicted due to being at the "bottom" of the mempool when the
        # mempool overflows and evicts by descendant score. It's important that the eviction doesn't
        # happen in the middle of package evaluation, as it can invalidate the coins cache.
        double_spent_utxo = self.wallet.get_utxo(confirmed_only=True)
        replaced_tx = self.wallet.send_self_transfer(
            from_node=node,
            utxo_to_spend=double_spent_utxo,
            fee_rate=mempoolmin_feerate,
            confirmed_only=True
        )
        # Already in mempool when package is submitted.
        assert replaced_tx["txid"] in node.getrawmempool()

        # This parent spends the above mempool transaction that exists when its inputs are first
        # looked up, but disappears later. It is rejected for being too low fee (but eligible for
        # reconsideration), and its inputs are cached. When the mempool transaction is evicted, its
        # coin is no longer available, but the cache could still contain the tx.
        cpfp_parent = self.wallet.create_self_transfer(
            utxo_to_spend=replaced_tx["new_utxo"],
            fee_rate=mempoolmin_feerate - Decimal('0.00001'),
            confirmed_only=True)

        self.wallet.rescan_utxos()

        # Parent that replaces the parent of cpfp_parent.
        replacement_tx = self.wallet.create_self_transfer(
            utxo_to_spend=double_spent_utxo,
            fee_rate=10*mempoolmin_feerate,
            confirmed_only=True
        )
        parent_utxos = [cpfp_parent["new_utxo"], replacement_tx["new_utxo"]]

        # Create a child spending everything, CPFPing the low-feerate parent.
        approx_child_vsize = self.wallet.create_self_transfer_multi(utxos_to_spend=parent_utxos)["tx"].get_vsize()
        cpfp_fee = (2 * mempoolmin_feerate / 1000) * (cpfp_parent["tx"].get_vsize() + approx_child_vsize) - cpfp_parent["fee"]
        child = self.wallet.create_self_transfer_multi(utxos_to_spend=parent_utxos, fee_per_output=int(cpfp_fee * COIN))
        # It's very important that the cpfp_parent is before replacement_tx so that its input (from
        # replaced_tx) is first looked up *before* replacement_tx is submitted.
        package_hex = [cpfp_parent["hex"], replacement_tx["hex"], child["hex"]]

        # Package should be submitted, temporarily exceeding maxmempool, and then evicted.
        assert_raises_rpc_error(-26, "bad-txns-inputs-missingorspent", node.submitpackage, package_hex)

        # Maximum size must never be exceeded.
        assert_greater_than(node.getmempoolinfo()["maxmempool"], node.getmempoolinfo()["bytes"])

        resulting_mempool_txids = node.getrawmempool()
        # The replacement should be successful.
        assert replacement_tx["txid"] in resulting_mempool_txids
        # The replaced tx and all of its descendants must not be in mempool.
        assert replaced_tx["txid"] not in resulting_mempool_txids
        assert cpfp_parent["txid"] not in resulting_mempool_txids
        assert child["txid"] not in resulting_mempool_txids


    def run_test(self):
        node = self.nodes[0]
        self.wallet = MiniWallet(node)
        miniwallet = self.wallet

        # Generate coins needed to create transactions in the subtests (excluding coins used in fill_mempool).
        self.generate(miniwallet, 20)

        relayfee = node.getnetworkinfo()['relayfee']
        self.log.info('Check that mempoolminfee is minrelaytxfee')
        assert_equal(node.getmempoolinfo()['minrelaytxfee'], Decimal('0.00001000'))
        assert_equal(node.getmempoolinfo()['mempoolminfee'], Decimal('0.00001000'))

        self.fill_mempool()

        # Deliberately try to create a tx with a fee less than the minimum mempool fee to assert that it does not get added to the mempool
        self.log.info('Create a mempool tx that will not pass mempoolminfee')
        assert_raises_rpc_error(-26, "mempool min fee not met", miniwallet.send_self_transfer, from_node=node, fee_rate=relayfee)

        self.log.info("Check that submitpackage allows cpfp of a parent below mempool min feerate")
        node = self.nodes[0]
        peer = node.add_p2p_connection(P2PTxInvStore())

        # Package with 2 parents and 1 child. One parent has a high feerate due to modified fees,
        # another is below the mempool minimum feerate but bumped by the child.
        tx_poor = miniwallet.create_self_transfer(fee_rate=relayfee)
        tx_rich = miniwallet.create_self_transfer(fee=0, fee_rate=0)
        node.prioritisetransaction(tx_rich["txid"], 0, int(DEFAULT_FEE * COIN))
        package_txns = [tx_rich, tx_poor]
        coins = [tx["new_utxo"] for tx in package_txns]
        tx_child = miniwallet.create_self_transfer_multi(utxos_to_spend=coins, fee_per_output=10000) #DEFAULT_FEE
        package_txns.append(tx_child)

        submitpackage_result = node.submitpackage([tx["hex"] for tx in package_txns])

        rich_parent_result = submitpackage_result["tx-results"][tx_rich["wtxid"]]
        poor_parent_result = submitpackage_result["tx-results"][tx_poor["wtxid"]]
        child_result = submitpackage_result["tx-results"][tx_child["tx"].getwtxid()]
        assert_fee_amount(poor_parent_result["fees"]["base"], tx_poor["tx"].get_vsize(), relayfee)
        assert_equal(rich_parent_result["fees"]["base"], 0)
        assert_equal(child_result["fees"]["base"], DEFAULT_FEE)
        # The "rich" parent does not require CPFP so its effective feerate is just its individual feerate.
        assert_fee_amount(DEFAULT_FEE, tx_rich["tx"].get_vsize(), rich_parent_result["fees"]["effective-feerate"])
        assert_equal(rich_parent_result["fees"]["effective-includes"], [tx_rich["wtxid"]])
        # The "poor" parent and child's effective feerates are the same, composed of their total
        # fees divided by their combined vsize.
        package_fees = poor_parent_result["fees"]["base"] + child_result["fees"]["base"]
        package_vsize = tx_poor["tx"].get_vsize() + tx_child["tx"].get_vsize()
        assert_fee_amount(package_fees, package_vsize, poor_parent_result["fees"]["effective-feerate"])
        assert_fee_amount(package_fees, package_vsize, child_result["fees"]["effective-feerate"])
        assert_equal([tx_poor["wtxid"], tx_child["tx"].getwtxid()], poor_parent_result["fees"]["effective-includes"])
        assert_equal([tx_poor["wtxid"], tx_child["tx"].getwtxid()], child_result["fees"]["effective-includes"])

        self.log.info('Test passing a value below the minimum (5 MB) to -maxmempool throws an error')
        self.stop_node(0)
        self.nodes[0].assert_start_raises_init_error(["-maxmempool=4"], "Error: -maxmempool must be at least 5 MB")

        self.test_mid_package_replacement()
        self.test_mid_package_eviction()


if __name__ == '__main__':
    MempoolLimitTest().main()
