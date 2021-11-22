#!/usr/bin/env python3
# Copyright (c) 2020-2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test error messages for 'getaddressinfo' and 'validateaddress' RPC commands."""

from test_framework.test_framework import BGLTestFramework

from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)

BECH32_VALID = 'bcrt1qtmp74ayg7p24uslctssvjm06q5phz4yrxucgnv'
BECH32_INVALID_BECH32 = 'bcrt1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqdmchcc'
BECH32_INVALID_BECH32M = 'bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7k35mrzd'
BECH32_INVALID_VERSION = 'bcrt130xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqynjegk'
BECH32_INVALID_SIZE = 'bcrt1s0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v8n0nx0muaewav25430mtr'
BECH32_INVALID_V0_SIZE = 'bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kqqq5k3my'
BECH32_INVALID_PREFIX = 'bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx'

BASE58_VALID = 'mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn'
BASE58_INVALID_PREFIX = '17VZNX1SN5NtKa8UQFxwQbFeFc3iqRYhem'

INVALID_ADDRESS = 'asfah14i8fajz0123f'

class InvalidAddressErrorMessageTest(BGLTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1

    def test_validateaddress(self):
        node = self.nodes[0]

        # Bech32
        info = node.validateaddress(BECH32_INVALID_SIZE)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid Bech32 address data size')

        info = node.validateaddress(BECH32_INVALID_PREFIX)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid prefix for Bech32 address')

        info = node.validateaddress(BECH32_INVALID_BECH32)
        assert not info['isvalid']
        assert_equal(info['error'], 'Version 1+ witness address must use Bech32m checksum')

        info = node.validateaddress(BECH32_INVALID_BECH32M)
        assert not info['isvalid']
        assert_equal(info['error'], 'Version 0 witness address must use Bech32 checksum')

        info = node.validateaddress(BECH32_INVALID_V0_SIZE)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid Bech32 v0 address data size')

        info = node.validateaddress(BECH32_VALID)
        assert info['isvalid']
        assert 'error' not in info

        info = node.validateaddress(BECH32_INVALID_VERSION)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid Bech32 address witness version')

    def test_validateaddress(self):
        # Invalid Bech32
        self.check_invalid(BECH32_INVALID_SIZE, 'Invalid Bech32 address data size')
        self.check_invalid(BECH32_INVALID_PREFIX, 'Not a valid Bech32 or Base58 encoding')
        self.check_invalid(BECH32_INVALID_BECH32, 'Version 1+ witness address must use Bech32m checksum')
        self.check_invalid(BECH32_INVALID_BECH32M, 'Version 0 witness address must use Bech32 checksum')
        self.check_invalid(BECH32_INVALID_VERSION, 'Invalid Bech32 address witness version')
        self.check_invalid(BECH32_INVALID_V0_SIZE, 'Invalid Bech32 v0 address data size')
        self.check_invalid(BECH32_TOO_LONG, 'Bech32 string too long', list(range(90, 108)))
        self.check_invalid(BECH32_ONE_ERROR, 'Invalid checksum', [9])
        self.check_invalid(BECH32_TWO_ERRORS, 'Invalid checksum', [22, 43])
        self.check_invalid(BECH32_ONE_ERROR_CAPITALS, 'Invalid checksum', [38])
        self.check_invalid(BECH32_NO_SEPARATOR, 'Missing separator')
        self.check_invalid(BECH32_INVALID_CHAR, 'Invalid Base 32 character', [8])
        self.check_invalid(BECH32_MULTISIG_TWO_ERRORS, 'Invalid checksum', [19, 30])
        self.check_invalid(BECH32_WRONG_VERSION, 'Invalid checksum', [5])

        # Valid Bech32
        self.check_valid(BECH32_VALID)
        self.check_valid(BECH32_VALID_CAPITALS)
        self.check_valid(BECH32_VALID_MULTISIG)

        # Invalid Base58
        self.check_invalid(BASE58_INVALID_PREFIX, 'Invalid prefix for Base58-encoded address')
        self.check_invalid(BASE58_INVALID_CHECKSUM, 'Invalid checksum or length of Base58 address')
        self.check_invalid(BASE58_INVALID_LENGTH, 'Invalid checksum or length of Base58 address')

        # Valid Base58
        self.check_valid(BASE58_VALID)

        # Invalid address format
        self.check_invalid(INVALID_ADDRESS, 'Not a valid Bech32 or Base58 encoding')
        self.check_invalid(INVALID_ADDRESS_2, 'Not a valid Bech32 or Base58 encoding')

    def test_getaddressinfo(self):
        node = self.nodes[0]

        assert_raises_rpc_error(-5, "Invalid Bech32 address data size", node.getaddressinfo, BECH32_INVALID_SIZE)

        assert_raises_rpc_error(-5, "Not a valid Bech32 or Base58 encoding", node.getaddressinfo, BECH32_INVALID_PREFIX)

        assert_raises_rpc_error(-5, "Invalid prefix for Base58-encoded address", node.getaddressinfo, BASE58_INVALID_PREFIX)

        assert_raises_rpc_error(-5, "Not a valid Bech32 or Base58 encoding", node.getaddressinfo, INVALID_ADDRESS)

    def run_test(self):
        self.test_validateaddress()

        if self.is_wallet_compiled():
            self.init_wallet(node=0)
            self.test_getaddressinfo()


if __name__ == '__main__':
    InvalidAddressErrorMessageTest().main()
