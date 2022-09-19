#!/usr/bin/env python3
# Copyright (c) 2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""A limited-functionality wallet, which may replace a real wallet in tests"""

from copy import deepcopy
from decimal import Decimal
from enum import Enum
from random import choice
from typing import (
    Any,
    List,
    Optional,
)
from test_framework.address import ADDRESS_BCRT1_P2WSH_OP_TRUE
from test_framework.descriptors import descsum_create
from test_framework.key import ECKey
from test_framework.messages import (
    COIN,
    COutPoint,
    CTransaction,
    CTxIn,
    CTxInWitness,
    CTxOut,
    tx_from_hex,
)
from test_framework.script import (
    CScript,
    LegacySignatureHash,
    OP_TRUE,
    OP_NOP,
    SIGHASH_ALL,
)
from test_framework.script_util import (
    key_to_p2pk_script,
    key_to_p2wpkh_script,
)
from test_framework.util import (
    assert_equal,
    assert_greater_than_or_equal,
)
from enum import Enum

DEFAULT_FEE = Decimal("0.0001")

class MiniWalletMode(Enum):
    """Determines the transaction type the MiniWallet is creating and spending.

    For most purposes, the default mode ADDRESS_OP_TRUE should be sufficient;
    it simply uses a fixed bech32 P2WSH address whose coins are spent with a
    witness stack of OP_TRUE, i.e. following an anyone-can-spend policy.
    However, if the transactions need to be modified by the user (e.g. prepending
    scriptSig for testing opcodes that are activated by a soft-fork), or the txs
    should contain an actual signature, the raw modes RAW_OP_TRUE and RAW_P2PK
    can be useful. Summary of modes:

                    |      output       |           |  tx is   | can modify |  needs
         mode       |    description    |  address  | standard | scriptSig  | signing
    ----------------+-------------------+-----------+----------+------------+----------
    ADDRESS_OP_TRUE | anyone-can-spend  |  bech32   |   yes    |    no      |   no
    RAW_OP_TRUE     | anyone-can-spend  |  - (raw)  |   no     |    yes     |   no
    RAW_P2PK        | pay-to-public-key |  - (raw)  |   yes    |    yes     |   yes
    """
    ADDRESS_OP_TRUE = 1
    RAW_OP_TRUE = 2
    RAW_P2PK = 3


class MiniWallet:
    def __init__(self, test_node, *, mode=MiniWalletMode.ADDRESS_OP_TRUE):
        self._test_node = test_node
        self._utxos = []
        self._priv_key = None
        self._address = None

        assert isinstance(mode, MiniWalletMode)
        if mode == MiniWalletMode.RAW_OP_TRUE:
            self._scriptPubKey = bytes(CScript([OP_TRUE]))
        elif mode == MiniWalletMode.RAW_P2PK:
            # use simple deterministic private key (k=1)
            self._priv_key = ECKey()
            self._priv_key.set((1).to_bytes(32, 'big'), True)
            pub_key = self._priv_key.get_pubkey()
            self._scriptPubKey = key_to_p2pk_script(pub_key.get_bytes())
        elif mode == MiniWalletMode.ADDRESS_OP_TRUE:
            self._address = ADDRESS_BCRT1_P2WSH_OP_TRUE
            self._scriptPubKey = bytes.fromhex(self._test_node.validateaddress(self._address)['scriptPubKey'])

    def _create_utxo(self, *, txid, vout, value, height):
        return {"txid": txid, "vout": vout, "value": value, "height": height}

    def get_balance(self):
        return sum(u['value'] for u in self._utxos)

    def rescan_utxos(self):
        """Drop all utxos and rescan the utxo set"""
        self._utxos = []
        res = self._test_node.scantxoutset(action="start", scanobjects=[f'addr({self._test_node.get_deterministic_priv_key().address})'])
        assert_equal(True, res['success'])
        for utxo in res['unspents']:
            self._utxos.append(self._create_utxo(txid=utxo["txid"], vout=utxo["vout"], value=utxo["amount"], height=utxo["height"]))

    def scan_tx(self, tx):
        """Scan the tx and adjust the internal list of owned utxos"""
        for spent in tx["vin"]:
            # Mark spent. This may happen when the caller has ownership of a
            # utxo that remained in this wallet. For example, by passing
            # mark_as_spent=False to get_utxo or by using an utxo returned by a
            # create_self_transfer* call.
            try:
                self.get_utxo(txid=spent["txid"], vout=spent["vout"])
            except StopIteration:
                pass
        for out in tx['vout']:
            if out['scriptPubKey']['hex'] == self._scriptPubKey.hex():
                self._utxos.append(self._create_utxo(txid=tx["txid"], vout=out["n"], value=out["value"], height=0))

    def sign_tx(self, tx, fixed_length=True):
        """Sign tx that has been created by MiniWallet in P2PK mode"""
        assert self._priv_key is not None
        (sighash, err) = LegacySignatureHash(CScript(self._scriptPubKey), tx, 0, SIGHASH_ALL)
        assert err is None
        # for exact fee calculation, create only signatures with fixed size by default (>49.89% probability):
        # 65 bytes: high-R val (33 bytes) + low-S val (32 bytes)
        # with the DER header/skeleton data of 6 bytes added, this leads to a target size of 71 bytes
        der_sig = b''
        while not len(der_sig) == 71:
            der_sig = self._priv_key.sign_ecdsa(sighash)
            if not fixed_length:
                break
        tx.vin[0].scriptSig = CScript([der_sig + bytes(bytearray([SIGHASH_ALL]))])
        tx.rehash()

    def generate(self, num_blocks, **kwargs):
        """Generate blocks with coinbase outputs to the internal address, and call rescan_utxos"""
        blocks = self._test_node.generatetoaddress(num_blocks, self._test_node.get_deterministic_priv_key().address, **kwargs)
        # Calling rescan_utxos here makes sure that after a generate the utxo
        # set is in a clean state. For example, the wallet will update
        # - if the caller consumed utxos, but never used them
        # - if the caller sent a transaction that is not mined or got rbf'd
        # - after block re-orgs
        # - the utxo height for mined mempool txs
        # - However, the wallet will not consider remaining mempool txs
        self.rescan_utxos()
        return blocks

    def get_scriptPubKey(self):
        return self._scriptPubKey

    def get_descriptor(self):
        return descsum_create(f'raw({self._scriptPubKey.hex()})')

    def get_address(self):
        return self._address

    def get_utxo(self, *, txid: str = '', vout: Optional[int] = None, mark_as_spent=True) -> dict:
        """
        Returns a utxo and marks it as spent (pops it from the internal list)

        Args:
        txid: get the first utxo we find from a specific transaction
        """
        self._utxos = sorted(self._utxos, key=lambda k: (k['value'], -k['height']))  # Put the largest utxo last
        if txid:
            utxo_filter: Any = filter(lambda utxo: txid == utxo['txid'], self._utxos)
        else:
            utxo_filter = reversed(self._utxos)  # By default the largest utxo
        if vout is not None:
            utxo_filter = filter(lambda utxo: vout == utxo['vout'], utxo_filter)
        index = self._utxos.index(next(utxo_filter))
        if mark_as_spent:
            return self._utxos.pop(index)
        else:
            return self._utxos[index]

    def get_utxos(self, *, mark_as_spent=True):
        """Returns the list of all utxos and optionally mark them as spent"""
        utxos = deepcopy(self._utxos)
        if mark_as_spent:
            self._utxos = []
        return utxos

    def send_self_transfer(self, *, from_node, **kwargs):
        """Create and send a tx with the specified fee_rate. Fee may be exact or at most one satoshi higher than needed."""
        tx = self.create_self_transfer(**kwargs)
        self.sendrawtransaction(from_node=from_node, tx_hex=tx['hex'])
        return tx

    def send_to(self, *, from_node, scriptPubKey, amount, fee=1000):
        """
        Create and send a tx with an output to a given scriptPubKey/amount,
        plus a change output to our internal address. To keep things simple, a
        fixed fee given in Satoshi is used.

        Note that this method fails if there is no single internal utxo
        available that can cover the cost for the amount and the fixed fee
        (the utxo with the largest value is taken).

        Returns a tuple (txid, n) referring to the created external utxo outpoint.
        """
        tx = self.create_self_transfer(fee_rate=0)["tx"]
        assert_greater_than_or_equal(tx.vout[0].nValue, amount + fee)
        tx.vout[0].nValue -= (amount + fee)           # change output -> MiniWallet
        tx.vout.append(CTxOut(amount, scriptPubKey))  # arbitrary output -> to be returned
        txid = self.sendrawtransaction(from_node=from_node, tx_hex=tx.serialize().hex())
        return txid, 1

    def send_self_transfer_multi(self, *, from_node, **kwargs):
        """Call create_self_transfer_multi and send the transaction."""
        tx = self.create_self_transfer_multi(**kwargs)
        txid = self.sendrawtransaction(from_node=from_node, tx_hex=tx.serialize().hex())
        return {'new_utxos': [self.get_utxo(txid=txid, vout=vout) for vout in range(len(tx.vout))],
                'txid': txid, 'hex': tx.serialize().hex(), 'tx': tx}

    def create_self_transfer_multi(
        self,
        *,
        utxos_to_spend: Optional[List[dict]] = None,
        num_outputs=1,
        amount_per_output=0,
        sequence=0,
        fee_per_output=1000,
    ):
        """
        Create and return a transaction that spends the given UTXOs and creates a
        certain number of outputs with equal amounts. The output amounts can be
        set by amount_per_output or automatically calculated with a fee_per_output.
        """
        utxos_to_spend = utxos_to_spend or [self.get_utxo()]
        sequence = [sequence] * len(utxos_to_spend) if type(sequence) is int else sequence
        assert_equal(len(utxos_to_spend), len(sequence))
        # create simple tx template (1 input, 1 output)
        tx = self.create_self_transfer(
            fee_rate=0,
            utxo_to_spend=utxos_to_spend[0])["tx"]

        # duplicate inputs, witnesses and outputs
        tx.vin = [deepcopy(tx.vin[0]) for _ in range(len(utxos_to_spend))]
        for txin, seq in zip(tx.vin, sequence):
            txin.nSequence = seq
        tx.wit.vtxinwit = [deepcopy(tx.wit.vtxinwit[0]) for _ in range(len(utxos_to_spend))]
        tx.vout = [deepcopy(tx.vout[0]) for _ in range(num_outputs)]

        # adapt input prevouts
        for i, utxo in enumerate(utxos_to_spend):
            tx.vin[i] = CTxIn(COutPoint(int(utxo['txid'], 16), utxo['vout']))

        # adapt output amounts (use fixed fee per output)
        inputs_value_total = sum([int(COIN * utxo['value']) for utxo in utxos_to_spend])
        outputs_value_total = inputs_value_total - fee_per_output * num_outputs
        for o in tx.vout:
            o.nValue = amount_per_output or (outputs_value_total // num_outputs)
        txid = tx.rehash()
        return {
            "new_utxos": [self._create_utxo(
                txid=txid,
                vout=i,
                value=Decimal(tx.vout[i].nValue) / COIN,
                height=0,
            ) for i in range(len(tx.vout))],
            "txid": txid,
            "hex": tx.serialize().hex(),
            "tx": tx,
        }

    def create_self_transfer(self, *, fee_rate=Decimal("0.003"), utxo_to_spend=None, locktime=0, sequence=0):
        """Create and return a tx with the specified fee_rate. Fee may be exact or at most one satoshi higher than needed."""
        utxo_to_spend = utxo_to_spend or self.get_utxo()
        if self._priv_key is None:
            vsize = Decimal(96)  # anyone-can-spend
        else:
            vsize = Decimal(168)  # P2PK (73 bytes scriptSig + 35 bytes scriptPubKey + 60 bytes other)
        send_value = utxo_to_spend["value"] - (fee_rate * vsize / 1000)
        assert send_value > 0

        tx = CTransaction()
        tx.vin = [CTxIn(COutPoint(int(utxo_to_spend['txid'], 16), utxo_to_spend['vout']), nSequence=sequence)]
        tx.vout = [CTxOut(int(COIN * send_value), bytearray(self._scriptPubKey))]
        tx.nLockTime = locktime
        if not self._address:
            # raw script
            if self._priv_key is not None:
                # P2PK, need to sign
                self.sign_tx(tx)
            else:
                # anyone-can-spend
                tx.vin[0].scriptSig = CScript([OP_NOP] * 35)  # pad to identical size
        else:
            tx.wit.vtxinwit = [CTxInWitness()]
            tx.wit.vtxinwit[0].scriptWitness.stack = [CScript([OP_TRUE])]
        tx_hex = tx.serialize().hex()

        assert_equal(tx.get_vsize(), vsize)
        new_utxo = self._create_utxo(txid=tx.rehash(), vout=0, value=send_value, height=0)

        return {"txid": new_utxo["txid"], "wtxid": tx.getwtxid(), "hex": tx_hex, "tx": tx, "new_utxo": new_utxo}

    def sendrawtransaction(self, *, from_node, tx_hex, maxfeerate=0, **kwargs):
        txid = from_node.sendrawtransaction(hexstring=tx_hex, maxfeerate=maxfeerate, **kwargs)
        self.scan_tx(from_node.decoderawtransaction(tx_hex))
        return txid


def random_p2wpkh():
    """Generate a random P2WPKH scriptPubKey. Can be used when a random destination is needed,
    but no compiled wallet is available (e.g. as replacement to the getnewaddress RPC)."""
    key = ECKey()
    key.generate()
    return key_to_p2wpkh_script(key.get_pubkey().get_bytes())


def make_chain(node, address, privkeys, parent_txid, parent_value, n=0, parent_locking_script=None, fee=DEFAULT_FEE):
    """Build a transaction that spends parent_txid.vout[n] and produces one output with
    amount = parent_value with a fee deducted.
    Return tuple (CTransaction object, raw hex, nValue, scriptPubKey of the output created).
    """
    inputs = [{"txid": parent_txid, "vout": n}]
    my_value = parent_value - Decimal("0.0001")
    outputs = {address : my_value}
    rawtx = node.createrawtransaction(inputs, outputs)
    prevtxs = [{
        "txid": parent_txid,
        "vout": n,
        "scriptPubKey": parent_locking_script,
        "amount": parent_value,
    }] if parent_locking_script else None
    signedtx = node.signrawtransactionwithkey(hexstring=rawtx, privkeys=privkeys, prevtxs=prevtxs)
    assert signedtx["complete"]
    tx = tx_from_hex(signedtx["hex"])
    return (tx, signedtx["hex"], my_value, tx.vout[0].scriptPubKey.hex())

def create_child_with_parents(node, address, privkeys, parents_tx, values, locking_scripts):
    """Creates a transaction that spends the first output of each parent in parents_tx."""
    num_parents = len(parents_tx)
    total_value = sum(values)
    inputs = [{"txid": tx.rehash(), "vout": 0} for tx in parents_tx]
    outputs = {address : total_value - num_parents * Decimal("0.0001")}
    rawtx_child = node.createrawtransaction(inputs, outputs)
    prevtxs = []
    for i in range(num_parents):
        prevtxs.append({"txid": parents_tx[i].rehash(), "vout": 0, "scriptPubKey": locking_scripts[i], "amount": values[i]})
    signedtx_child = node.signrawtransactionwithkey(hexstring=rawtx_child, privkeys=privkeys, prevtxs=prevtxs)
    assert signedtx_child["complete"]
    return signedtx_child["hex"]

def create_raw_chain(node, first_coin, address, privkeys, chain_length=25):
    """Helper function: create a "chain" of chain_length transactions. The nth transaction in the
    chain is a child of the n-1th transaction and parent of the n+1th transaction.
    """
    parent_locking_script = None
    txid = first_coin["txid"]
    chain_hex = []
    chain_txns = []
    value = first_coin["amount"]

    for _ in range(chain_length):
        (tx, txhex, value, parent_locking_script) = make_chain(node, address, privkeys, txid, value, 0, parent_locking_script)
        txid = tx.rehash()
        chain_hex.append(txhex)
        chain_txns.append(tx)

    return (chain_hex, chain_txns)

def bulk_transaction(tx, node, target_weight, privkeys, prevtxs=None):
    """Pad a transaction with extra outputs until it reaches a target weight (or higher).
    returns CTransaction object
    """
    tx_heavy = deepcopy(tx)
    assert_greater_than_or_equal(target_weight, tx_heavy.get_weight())
    while tx_heavy.get_weight() < target_weight:
        random_spk = "6a4d0200"  # OP_RETURN OP_PUSH2 512 bytes
        for _ in range(512*2):
            random_spk += choice("0123456789ABCDEF")
        tx_heavy.vout.append(CTxOut(0, bytes.fromhex(random_spk)))
    # Re-sign the transaction
    if privkeys:
        signed = node.signrawtransactionwithkey(tx_heavy.serialize().hex(), privkeys, prevtxs)
        return tx_from_hex(signed["hex"])
    # OP_TRUE
    tx_heavy.wit.vtxinwit = [CTxInWitness()]
    tx_heavy.wit.vtxinwit[0].scriptWitness.stack = [CScript([OP_TRUE])]
    return tx_heavy
