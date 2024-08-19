#!/usr/bin/env python3
# Copyright (c) 2017-2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test external signer.
Verify that a BGLd node can use an external signer command
See also rpc_signer.py for tests without wallet context."""
import os
import platform

from test_framework.test_framework import BGLTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)


class WalletSignerTest(BGLTestFramework):
    def add_options(self, parser):
        self.add_wallet_options(parser, legacy=False)

    def mock_signer_path(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocks', 'signer.py')
        if platform.system() == "Windows":
            return "py -3 " + path
        else:
            return path

    def mock_invalid_signer_path(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocks', 'invalid_signer.py')
        if platform.system() == "Windows":
            return "py -3 " + path
        else:
            return path

    def mock_multi_signers_path(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mocks', 'multi_signers.py')
        if platform.system() == "Windows":
            return "py -3 " + path
        else:
            return path

    def set_test_params(self):
        print("set_test_params", self.mock_signer_path())
        self.num_nodes = 2

        self.extra_args = [
            [],
            [f"-signer={self.mock_signer_path()}", '-keypool=10'],
        ]

    def skip_test_if_missing_module(self):
        self.skip_if_no_external_signer()
        self.skip_if_no_wallet()

    def set_mock_result(self, node, res):
        with open(os.path.join(node.cwd, "mock_result"), "w", encoding="utf8") as f:
            f.write(res)

    def clear_mock_result(self, node):
        os.remove(os.path.join(node.cwd, "mock_result"))

    def run_test(self):
        self.test_valid_signer()
        self.restart_node(1, [f"-signer={self.mock_invalid_signer_path()}", "-keypool=10"])
        self.test_invalid_signer()

    def test_valid_signer(self):
        self.log.debug(f"-signer={self.mock_signer_path()}")

        # Create new wallets for an external signer.
        # disable_private_keys and descriptors must be true:
        assert_raises_rpc_error(-4, "Private keys must be disabled when using an external signer", self.nodes[1].createwallet, wallet_name='not_hww', disable_private_keys=False, descriptors=True, external_signer=True)
        if self.is_bdb_compiled():
            assert_raises_rpc_error(-4, "Descriptor support must be enabled when using an external signer", self.nodes[1].createwallet, wallet_name='not_hww', disable_private_keys=True, descriptors=False, external_signer=True)
        else:
            assert_raises_rpc_error(-4, "Compiled without bdb support (required for legacy wallets)", self.nodes[1].createwallet, wallet_name='not_hww', disable_private_keys=True, descriptors=False, external_signer=True)

        self.nodes[1].createwallet(wallet_name='hww', disable_private_keys=True, descriptors=True, external_signer=True)
        hww = self.nodes[1].get_wallet_rpc('hww')
        assert_equal(hww.getwalletinfo()["external_signer"], True)

        # Flag can't be set afterwards (could be added later for non-blank descriptor based watch-only wallets)
        self.nodes[1].createwallet(wallet_name='not_hww', disable_private_keys=True, descriptors=True, external_signer=False)
        not_hww = self.nodes[1].get_wallet_rpc('not_hww')
        assert_equal(not_hww.getwalletinfo()["external_signer"], False)
        assert_raises_rpc_error(-8, "Wallet flag is immutable: external_signer", not_hww.setwalletflag, "external_signer", True)

        # assert_raises_rpc_error(-4, "Multiple signers found, please specify which to use", wallet_name='not_hww', disable_private_keys=True, descriptors=True, external_signer=True)

        # TODO: Handle error thrown by script
        # self.set_mock_result(self.nodes[1], "2")
        # assert_raises_rpc_error(-1, 'Unable to parse JSON',
        #     self.nodes[1].createwallet, wallet_name='not_hww2', disable_private_keys=True, descriptors=True, external_signer=False
        # )
        # self.clear_mock_result(self.nodes[1])

        assert_equal(hww.getwalletinfo()["keypoolsize"], 40)

        address1 = hww.getnewaddress(address_type="bech32")
        assert_equal(address1, "rbgl1qm90ugl4d48jv8n6e5t9ln6t9zlpm5th67ecp7z")
        address_info = hww.getaddressinfo(address1)
        assert_equal(address_info['solvable'], True)
        assert_equal(address_info['ismine'], True)
        assert_equal(address_info['hdkeypath'], "m/84h/1h/0h/0/0")

        address2 = hww.getnewaddress(address_type="p2sh-segwit")
        assert_equal(address2, "MHLLa9DQyiTkwrTMjKL3NSikudmoifhjQF")
        address_info = hww.getaddressinfo(address2)
        assert_equal(address_info['solvable'], True)
        assert_equal(address_info['ismine'], True)
        assert_equal(address_info['hdkeypath'], "m/49h/1h/0h/0/0")

        address3 = hww.getnewaddress(address_type="legacy")
        assert_equal(address3, "F2JsqNDPxUREheXBJE9vffuN4E4gCH1yVC")
        address_info = hww.getaddressinfo(address3)
        assert_equal(address_info['solvable'], True)
        assert_equal(address_info['ismine'], True)
        assert_equal(address_info['hdkeypath'], "m/44h/1h/0h/0/0")

        self.log.info('Test walletdisplayaddress')
        for address in [address1, address2, address3]:
            result = hww.walletdisplayaddress(address)
            assert_equal(result, {"address": address})

        # Handle error thrown by script
        self.set_mock_result(self.nodes[1], "2")
        assert_raises_rpc_error(-1, 'RunCommandParseJSON error',
            hww.walletdisplayaddress, address1
        )
        self.clear_mock_result(self.nodes[1])

        # Returned address MUST match:
        address_fail = hww.getnewaddress(address_type="bech32")
        assert_equal(address_fail, "rbgl1ql7zg7ukh3dwr25ex2zn9jse926f27xy2tae0j3")
        assert_raises_rpc_error(-1, 'Signer echoed unexpected address wrong_address',
            hww.walletdisplayaddress, address_fail
        )

        self.log.info('Prepare mock PSBT')
        self.nodes[0].sendtoaddress(address1, 1)
        self.generate(self.nodes[0], 1)

        # Load private key into wallet to generate a signed PSBT for the mock
        self.nodes[1].createwallet(wallet_name="mock", disable_private_keys=False, blank=True, descriptors=True)
        mock_wallet = self.nodes[1].get_wallet_rpc("mock")
        assert mock_wallet.getwalletinfo()['private_keys_enabled']

        result = mock_wallet.importdescriptors([{
            "desc": "wpkh([00000001/84'/1'/0']tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0/*)#rweraev0",
            "timestamp": 0,
            "range": [0,1],
            "internal": False,
            "active": True
        },
        {
            "desc": "wpkh([00000001/84'/1'/0']tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/*)#j6uzqvuh",
            "timestamp": 0,
            "range": [0, 0],
            "internal": True,
            "active": True
        }])
        assert_equal(result[0], {'success': True})
        assert_equal(result[1], {'success': True})
        assert_equal(mock_wallet.getwalletinfo()["txcount"], 1)
        dest = self.nodes[0].getnewaddress(address_type='bech32')
        mock_psbt = mock_wallet.walletcreatefundedpsbt([], {dest:0.5}, 0, {}, True)['psbt']
        mock_psbt_signed = mock_wallet.walletprocesspsbt(psbt=mock_psbt, sign=True, sighashtype="ALL", bip32derivs=True)
        mock_tx = mock_psbt_signed["hex"]
        assert mock_wallet.testmempoolaccept([mock_tx])[0]["allowed"]

        # # Create a new wallet and populate with specific public keys, in order
        # # to work with the mock signed PSBT.
        # self.nodes[1].createwallet(wallet_name="hww4", disable_private_keys=True, descriptors=True, external_signer=True)
        # hww4 = self.nodes[1].get_wallet_rpc("hww4")
        #
        # descriptors = [{
        #     "desc": "wpkh([00000001/84h/1h/0']tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/0/*)#x30uthjs",
        #     "timestamp": "now",
        #     "range": [0, 1],
        #     "internal": False,
        #     "watchonly": True,
        #     "active": True
        # },
        # {
        #     "desc": "wpkh([00000001/84h/1h/0']tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1/*)#h92akzzg",
        #     "timestamp": "now",
        #     "range": [0, 0],
        #     "internal": True,
        #     "watchonly": True,
        #     "active": True
        # }]

        # result = hww4.importdescriptors(descriptors)
        # assert_equal(result[0], {'success': True})
        # assert_equal(result[1], {'success': True})
        assert_equal(hww.getwalletinfo()["txcount"], 1)

        assert hww.testmempoolaccept([mock_tx])[0]["allowed"]

        with open(os.path.join(self.nodes[1].cwd, "mock_psbt"), "w", encoding="utf8") as f:
            f.write(mock_psbt_signed["psbt"])

        self.log.info('Test send using hww1')

        # Don't broadcast transaction yet so the RPC returns the raw hex
        res = hww.send(outputs={dest:0.5},add_to_wallet=False)
        assert res["complete"]
        assert_equal(res["hex"], mock_tx)

        self.log.info('Test sendall using hww1')

        res = hww.sendall(recipients=[{dest:0.5}, hww.getrawchangeaddress()], add_to_wallet=False)
        assert res["complete"]
        assert_equal(res["hex"], mock_tx)

        # # Handle error thrown by script
        # self.set_mock_result(self.nodes[4], "2")
        # assert_raises_rpc_error(-1, 'Unable to parse JSON',
        #     hww4.signerprocesspsbt, psbt_orig, "00000001"
        # )
        # self.clear_mock_result(self.nodes[4])

    def test_invalid_signer(self):
        self.log.debug(f"-signer={self.mock_invalid_signer_path()}")
        self.log.info('Test invalid external signer')
        assert_raises_rpc_error(-1, "Invalid descriptor", self.nodes[1].createwallet, wallet_name='hww_invalid', disable_private_keys=True, descriptors=True, external_signer=True)

if __name__ == '__main__':
    WalletSignerTest().main()
