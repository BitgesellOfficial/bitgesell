#!/usr/bin/env python3
# Copyright (c) 2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Stress tests related to node initialization."""
import random
import time
import os
from pathlib import Path

from test_framework.test_framework import BitcoinTestFramework, SkipTest
from test_framework.test_node import ErrorMatch
from test_framework.util import assert_equal


class InitStressTest(BitcoinTestFramework):
    """
    Ensure that initialization can be interrupted at a number of points and not impair
    subsequent starts.
    """

    def set_test_params(self):
        self.setup_clean_chain = False
        self.num_nodes = 1

    def run_test(self):
        """
        - test terminating initialization after seeing a certain log line.
        - test terminating init after seeing a random number of log lines.
        - test removing certain essential files to test startup error paths.
        """
        # TODO: skip Windows for now since it isn't clear how to SIGTERM.
        #
        # Windows doesn't support `process.terminate()`.
        # and other approaches (like below) don't work:
        #
        #   os.kill(node.process.pid, signal.CTRL_C_EVENT)
        if os.name == 'nt':
            raise SkipTest("can't SIGTERM on Windows")

        self.stop_node(0)
        node = self.nodes[0]

        def sigterm_node():
            node.process.terminate()
            node.process.wait()
            node.debug_log_path.unlink()
            node.debug_log_path.touch()

        def check_clean_start():
            """Ensure that node restarts successfully after various interrupts."""
            # TODO: add -txindex=1 to fully test index initiatlization.
            # See https://github.com/bitcoin/bitcoin/pull/23289#discussion_r735159180 for
            # a discussion of the related bug.
            node.start()
            node.wait_for_rpc_connection()
            assert_equal(200, node.getblockcount())

        lines_to_terminate_after = [
            'Validating signatures for all blocks',
            'scheduler thread start',
            'Starting HTTP server',
            'Loading P2P addresses',
            'Loading banlist',
            'Loading block index',
            'Switching active chainstate',
            'Checking all blk files are present',
            'Loaded best chain:',
            'init message: Verifying blocks',
            'init message: Starting network threads',
            'net thread start',
            'addcon thread start',
            'loadblk thread start',
            # TODO: reenable - see above TODO
            # 'txindex thread start',
            'msghand thread start'
        ]
        if self.is_wallet_compiled():
            lines_to_terminate_after.append('Verifying wallet')

        for terminate_line in lines_to_terminate_after:
            self.log.info(f"Starting node and will exit after line '{terminate_line}'")
            node.start(
                # TODO: add -txindex=1 to fully test index initiatlization.
                # extra_args=['-txindex=1'],
            )
            logfile = open(node.debug_log_path, 'r', encoding='utf8')

            MAX_SECS_TO_WAIT = 30
            start = time.time()
            num_lines = 0

            while True:
                line = logfile.readline()
                if line:
                    num_lines += 1

                if line and terminate_line.lower() in line.lower():
                    self.log.debug(f"Terminating node after {num_lines} log lines seen")
                    sigterm_node()
                    break

                if (time.time() - start) > MAX_SECS_TO_WAIT:
                    raise AssertionError(
                        f"missed line {terminate_line}; terminating now after {num_lines} lines")

                if node.process.poll() is not None:
                    raise AssertionError(f"node failed to start (line: '{terminate_line}')")

        check_clean_start()
        num_total_logs = len(node.debug_log_path.read_text().splitlines())
        self.stop_node(0)

        self.log.info(
            f"Terminate at some random point in the init process (max logs: {num_total_logs})")

        for _ in range(40):
            terminate_after = random.randint(1, num_total_logs)
            self.log.debug(f"Starting node and will exit after {terminate_after} lines")
            node.start(
                # TODO: add -txindex=1 to fully test index initiatlization.
                # extra_args=['-txindex=1'],
            )
            logfile = open(node.debug_log_path, 'r', encoding='utf8')

            MAX_SECS_TO_WAIT = 10
            start = time.time()
            num_lines = 0

            while True:
                line = logfile.readline()
                if line:
                    num_lines += 1

                if num_lines >= terminate_after or (time.time() - start) > MAX_SECS_TO_WAIT:
                    self.log.debug(f"Terminating node after {num_lines} log lines seen")
                    sigterm_node()
                    break

                if node.process.poll() is not None:
                    raise AssertionError("node failed to start")

        check_clean_start()
        self.stop_node(0)

        self.log.info("Test startup errors after removing certain essential files")

        files_to_disturb = {
            'blocks/index/*.ldb': 'Error opening block database.',
            'chainstate/*.ldb': 'Error opening block database.',
            'blocks/blk*.dat': 'Error loading block database.',
        }

        for file_patt, err_fragment in files_to_disturb.items():
            target_file = list(node.chain_path.glob(file_patt))[0]

            self.log.info(f"Tweaking file to ensure failure {target_file}")
            bak_path = str(target_file) + ".bak"
            target_file.rename(bak_path)

            # TODO: at some point, we should test perturbing the files instead of removing
            # them, e.g.
            #
            # contents = target_file.read_bytes()
            # tweaked_contents = bytearray(contents)
            # tweaked_contents[50:250] = b'1' * 200
            # target_file.write_bytes(bytes(tweaked_contents))
            #
            # At the moment I can't get this to work (bitcoind loads successfully?) so
            # investigate doing this later.

            node.assert_start_raises_init_error(
                # TODO: add -txindex=1 to fully test index initiatlization.
                # extra_args=['-txindex=1'],
                expected_msg=err_fragment,
                match=ErrorMatch.PARTIAL_REGEX,
            )

            self.log.info(f"Restoring file from {bak_path} and restarting")
            Path(bak_path).rename(target_file)
            check_clean_start()
            self.stop_node(0)


if __name__ == '__main__':
    InitStressTest().main()
