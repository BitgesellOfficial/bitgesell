#!/usr/bin/env python3
# Copyright (c) 2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import random
from enum import Enum

from test_framework.messages import MAGIC_BYTES
from test_framework.p2p import P2PInterface
from test_framework.test_framework import BGLTestFramework
from test_framework.util import random_bitflip
from test_framework.v2_p2p import (
    EncryptedP2PState,
    MAX_GARBAGE_LEN,
)


class TestType(Enum):
    """ Scenarios to be tested:

    1. EARLY_KEY_RESPONSE - The responder needs to wait until one byte is received which does not match the 16 bytes
    consisting of network magic followed by "version\x00\x00\x00\x00\x00" before sending out its ellswift + garbage bytes
    2. EXCESS_GARBAGE - Disconnection happens when > MAX_GARBAGE_LEN bytes garbage is sent
    3. WRONG_GARBAGE_TERMINATOR - Disconnection happens when incorrect garbage terminator is sent
    """
    EARLY_KEY_RESPONSE = 0
    EXCESS_GARBAGE = 1
    WRONG_GARBAGE_TERMINATOR = 2


class EarlyKeyResponseState(EncryptedP2PState):
    """ Modify v2 P2P protocol functions for testing EARLY_KEY_RESPONSE scenario"""
    def __init__(self, initiating, net):
        super().__init__(initiating=initiating, net=net)
        self.can_data_be_received = False  # variable used to assert if data is received on recvbuf.

    def initiate_v2_handshake(self):
        """Send ellswift and garbage bytes in 2 parts when TestType = (EARLY_KEY_RESPONSE)"""
        self.generate_keypair_and_garbage()
        return b""


class ExcessGarbageState(EncryptedP2PState):
    """Generate > MAX_GARBAGE_LEN garbage bytes"""
    def generate_keypair_and_garbage(self):
        garbage_len = MAX_GARBAGE_LEN + random.randrange(1, MAX_GARBAGE_LEN + 1)
        return super().generate_keypair_and_garbage(garbage_len)


class WrongGarbageTerminatorState(EncryptedP2PState):
    """Add option for sending wrong garbage terminator"""
    def generate_keypair_and_garbage(self):
        garbage_len = random.randrange(MAX_GARBAGE_LEN//2)
        return super().generate_keypair_and_garbage(garbage_len)

    def complete_handshake(self, response):
        length, handshake_bytes = super().complete_handshake(response)
        # first 16 bytes returned by complete_handshake() is the garbage terminator
        wrong_garbage_terminator = random_bitflip(handshake_bytes[:16])
        return length, wrong_garbage_terminator + handshake_bytes[16:]


class MisbehavingV2Peer(P2PInterface):
    """Custom implementation of P2PInterface which uses modified v2 P2P protocol functions for testing purposes."""
    def __init__(self, test_type):
        super().__init__()
        self.test_type = test_type

    def connection_made(self, transport):
        if self.test_type == TestType.EARLY_KEY_RESPONSE:
            self.v2_state = EarlyKeyResponseState(initiating=True, net='regtest')
        elif self.test_type == TestType.EXCESS_GARBAGE:
            self.v2_state = ExcessGarbageState(initiating=True, net='regtest')
        elif self.test_type == TestType.WRONG_GARBAGE_TERMINATOR:
            self.v2_state = WrongGarbageTerminatorState(initiating=True, net='regtest')
        super().connection_made(transport)

    def data_received(self, t):
        if self.test_type == TestType.EARLY_KEY_RESPONSE:
            # check that data can be received on recvbuf only when mismatch from V1_PREFIX happens
            assert self.v2_state.can_data_be_received
        else:
            super().data_received(t)


class EncryptedP2PMisbehaving(BGLTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.extra_args = [["-v2transport=1", "-peertimeout=3"]]

    def run_test(self):
        self.test_earlykeyresponse()
        self.test_v2disconnection()

    def test_earlykeyresponse(self):
        self.log.info('Sending ellswift bytes in parts to ensure that response from responder is received only when')
        self.log.info('ellswift bytes have a mismatch from the 16 bytes(network magic followed by "version\\x00\\x00\\x00\\x00\\x00")')
        node0 = self.nodes[0]
        self.log.info('Sending first 4 bytes of ellswift which match network magic')
        self.log.info('If a response is received, assertion failure would happen in our custom data_received() function')
        peer1 = node0.add_p2p_connection(MisbehavingV2Peer(TestType.EARLY_KEY_RESPONSE), wait_for_verack=False, send_version=False, supports_v2_p2p=True, wait_for_v2_handshake=False)
        peer1.send_raw_message(MAGIC_BYTES['regtest'])
        self.log.info('Sending remaining ellswift and garbage which are different from V1_PREFIX. Since a response is')
        self.log.info('expected now, our custom data_received() function wouldn\'t result in assertion failure')
        peer1.v2_state.can_data_be_received = True
        peer1.send_raw_message(peer1.v2_state.ellswift_ours[4:] + peer1.v2_state.sent_garbage)
        with node0.assert_debug_log(['V2 handshake timeout peer=0']):
            peer1.wait_for_disconnect(timeout=5)
        self.log.info('successful disconnection since modified ellswift was sent as response')

    def test_v2disconnection(self):
        # test v2 disconnection scenarios
        node0 = self.nodes[0]
        expected_debug_message = [
            [],  # EARLY_KEY_RESPONSE
            ["V2 transport error: missing garbage terminator, peer=1"],  # EXCESS_GARBAGE
            ["V2 handshake timeout peer=2"],  # WRONG_GARBAGE_TERMINATOR
        ]
        for test_type in TestType:
            if test_type == TestType.EARLY_KEY_RESPONSE:
                continue
            with node0.assert_debug_log(expected_debug_message[test_type.value], timeout=5):
                peer = node0.add_p2p_connection(MisbehavingV2Peer(test_type), wait_for_verack=False, send_version=False, supports_v2_p2p=True, expect_success=False)
                peer.wait_for_disconnect()
            self.log.info(f"Expected disconnection for {test_type.name}")


if __name__ == '__main__':
    EncryptedP2PMisbehaving().main()
