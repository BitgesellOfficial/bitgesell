#!/usr/bin/env python3
# Copyright (c) 2023 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test validateaddress for main chain"""

from test_framework.test_framework import BGLTestFramework

from test_framework.util import assert_equal

INVALID_DATA = [
    # BIP 173
    (
        "tc1qw508d6qejxtdg4y5r3zarvary0c5xw7kg3g4ty",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # Invalid hrp
        [],
    ),
    ("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5", "Invalid or unsupported Segwit (Bech32) or Base58 encoding.", []),
    (
        "BGL13W508D6QEJXTDG4Y5R3ZARVARY0C5XW7KN40WF2",
        "Invalid checksum",
        [],
    ),
    (
        "bgl1rw5uspcuh",
        "Invalid checksum",  # Invalid program length
        [],
    ),
    (
        "bgl10w508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kw5rljs90",
        "Invalid checksum",  # Invalid program length
        [],
    ),
    (
        "BC1QR508D6QEJXTDG4Y5R3ZARVARYV98GJ9P",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",
        [],
    ),
    (
        "tbg1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sL5k7",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Mixed case
        [],
    ),
    (
        "BGL1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3t4",
        "Invalid character or mixed case",  # bc1, Mixed case, not in BIP 173 test vectors
        [41],
    ),
    (
        "bgl1qq27hkf2zkwkxru4smxkwrtmsyumkpw84sx2x73",
        "Invalid checksum",  # Wrong padding
        [],
    ),
    (
        "tbg1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3pjxtptv",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Non-zero padding in 8-to-5 conversion
        [],
    ),
    ("b1gmk9yu", "Invalid checksum or length of Base58 address (P2PKH or P2SH)", []),
    # BIP 350
    (
        "tc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq5zuyut",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # Invalid human-readable part
        [],
    ),
    (
        "bgl1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqh2y7hde",
        "Invalid checksum",  # Invalid checksum (Bech32 instead of Bech32m)
        [],
    ),
    (
        "tbgl1z0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqglt7rfa1",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Invalid checksum (Bech32 instead of Bech32m)
        [],
    ),
    (
        "BGL1S0XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7E2VQ54WELL",
        "Invalid checksum",  # Invalid checksum (Bech32 instead of Bech32m)
        [],
    ),
    (
        "bgl1qw508d6qejxtdg4y5r3zarvary0c5xw7kemeawh1a",
        "Invalid separator position",  # Invalid checksum (Bech32m instead of Bech32)
        [43],
    ),
    (
        "tbgl1q0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq24jc47",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Invalid checksum (Bech32m instead of Bech32)
        [],
    ),
    (
        "bgl1p38j9r5y49hruaue7wxjce0updqjuyyx0kh56v8s25huc6995vvpql3jow4x2",
        "Invalid Base 32 character",  # Invalid character in checksum
        [60],
    ),
    (
        "BGL130XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQ7ZWS8R2M",
        "Invalid checksum",
        [],
    ),
    ("bgl1pw5dgrnzvk4", "Invalid checksum", []),
    (
        "bgl1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v8n0nx0muaewav253zgeavak",
        "Invalid checksum",
        [],
    ),
    (
        "BGL1QR508D6QEJXTDG4Y5R3ZARVARYV98GJ9PTD",
        "Invalid checksum",
        [],
    ),
    (
        "tbgl1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vq47Zagq33",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Mixed case
        [],
    ),
    (
        "bgl1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v07qwwzcrf4e",
        "Invalid checksum",  # zero padding of more than 4 bits
        [],
    ),
    (
        "tbgl1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hl2cz7vpggkg4j",
        "Invalid or unsupported Segwit (Bech32) or Base58 encoding.",  # tb1, Non-zero padding in 8-to-5 conversion
        [],
    ),
    ("bgl1gmk9yufg", "Invalid checksum", []),
]
VALID_DATA = [
    # BIP 350
    (
        "bgl1qzfw3pge25gwfk7308cmjsq8qjkgv9re36aawuu",
        "0014125d10a32aa21c9b7a2f3e372800e09590c28f31",
    ),
    # (
    #   "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7",
    #   "00201863143c14c5166804bd19203356da136c985678cd4d27a1b8c6329604903262",
    # ),
    (
        "bgl1q4gs8sd2tlukt7v9p2twxqancp9rr3t5r0fmxjl",
        "0014aa2078354bff2cbf30a152dc607678094638ae83",
    ),
    (
        "bgl1q280e3m87lp67ezp4hra3dlpded5h0eh3e8xz3l",
        "001451df98ecfef875ec8835b8fb16fc2dcb6977e6f1",
    ),
    ("bgl1qhf80v4tm4hs5hj76kdggwsfv2ua9f27a4mqg2z", "0014ba4ef6557bade14bcbdab35087412c573a54abdd"),
    ("bgl1qu9aya7kn5q4dyhcj47ypg6ye8k87jkqyzqctup", "0014e17a4efad3a02ad25f12af881468993d8fe95804"),
    # (
    #   "tb1qqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesrxh6hy",
    #   "0020000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    # ),
    (
        "bgl1qu9aya7kn5q4dyhcj47ypg6ye8k87jkqyzqctup",
        "0014e17a4efad3a02ad25f12af881468993d8fe95804",
    ),
    # (
    #   "tb1pqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesf3hn0c",
    #   "5120000000c4a5cad46221b2a187905e5266362b99d5e91c6ce24d165dab93e86433",
    # ),
    (
        "bgl1q4stxmmza3jkgeaq2c6lj3jwwej3020k8cvtl84",
        "0014ac166dec5d8cac8cf40ac6bf28c9cecca2f53ec7",
    ),
    (
        "bgl1qad89ple04k7lafrzw0kksjwfccg3uvyvhfxu5r",
        "0014eb4e50ff2fadbdfea46273ed6849c9c6111e308c",
    ),
]


class ValidateAddressMainTest(BGLTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.chain = ""  # main
        self.num_nodes = 1
        self.extra_args = [["-prune=899"]] * self.num_nodes

    def check_valid(self, addr, spk):
        info = self.nodes[0].validateaddress(addr)
        assert_equal(info["isvalid"], True)
        assert_equal(info["scriptPubKey"], spk)
        assert "error" not in info
        assert "error_locations" not in info

    def check_invalid(self, addr, error_str, error_locations):
        res = self.nodes[0].validateaddress(addr)
        assert_equal(res["isvalid"], False)
        assert_equal(res["error"], error_str)
        assert_equal(res["error_locations"], error_locations)

    def test_validateaddress(self):
        for (addr, error, locs) in INVALID_DATA:
            self.check_invalid(addr, error, locs)
        for (addr, spk) in VALID_DATA:
            self.check_valid(addr, spk)

    def run_test(self):
        self.test_validateaddress()


if __name__ == "__main__":
    ValidateAddressMainTest().main()
