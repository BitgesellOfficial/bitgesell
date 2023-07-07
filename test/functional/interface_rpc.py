#!/usr/bin/env python3
# Copyright (c) 2018-2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Tests some generic aspects of the RPC interface."""

import os
from test_framework.authproxy import JSONRPCException
from test_framework.test_framework import BGLTestFramework
from test_framework.util import assert_equal, assert_greater_than_or_equal

def expect_http_status(expected_http_status, expected_rpc_code,
                       fcn, *args):
    try:
        fcn(*args)
        raise AssertionError(f"Expected RPC error {expected_rpc_code}, got none")
    except JSONRPCException as exc:
        assert_equal(exc.error["code"], expected_rpc_code)
        assert_equal(exc.http_status, expected_http_status)


def test_work_queue_getblock(node, got_exceeded_error):
    while not got_exceeded_error:
        try:
            node.cli("waitfornewblock", "500").send_cli()
        except subprocess.CalledProcessError as e:
            assert_equal(e.output, 'error: Server response: Work queue depth exceeded\n')
            got_exceeded_error.append(True)


class RPCInterfaceTest(BGLTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.supports_cli = False

    def test_getrpcinfo(self):
        self.log.info("Testing getrpcinfo...")

        info = self.nodes[0].getrpcinfo()
        assert_equal(len(info['active_commands']), 1)

        command = info['active_commands'][0]
        assert_equal(command['method'], 'getrpcinfo')
        assert_greater_than_or_equal(command['duration'], 0)
        assert_equal(info['logpath'], os.path.join(self.nodes[0].chain_path, 'debug.log'))

    def test_batch_request(self):
        self.log.info("Testing basic JSON-RPC batch request...")

        results = self.nodes[0].batch([
            # A basic request that will work fine.
            {"method": "getblockcount", "id": 1},
            # Request that will fail.  The whole batch request should still
            # work fine.
            {"method": "invalidmethod", "id": 2},
            # Another call that should succeed.
            {"method": "getblockhash", "params": [0]},
            # Invalid request format
            {"pizza": "sausage"}
        ]
        results = [
            {"result": 0},
            {"error": {"code": RPC_METHOD_NOT_FOUND, "message": "Method not found"}},
            {"result": "0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206"},
            {"error": {"code": RPC_INVALID_REQUEST, "message": "Missing method"}},
        ]

        request = []
        response = []
        for idx, (call, result) in enumerate(zip(calls, results), 1):
            options = call_options(idx)
            if options is None:
                continue
            request.append(format_request(options, idx, call))
            response.append(format_response(options, idx, result))

        rpc_response, http_status = send_json_rpc(self.nodes[0], request)
        assert_equal(http_status, 200)
        assert_equal(rpc_response, response)

    def test_batch_requests(self):
        self.log.info("Testing empty batch request...")
        self.test_batch_request(lambda idx: None)

        self.log.info("Testing basic JSON-RPC 2.0 batch request...")
        self.test_batch_request(lambda idx: BatchOptions(version=2))

        self.log.info("Testing JSON-RPC 2.0 batch with notifications...")
        self.test_batch_request(lambda idx: BatchOptions(version=2, notification=idx < 2))

        self.log.info("Testing JSON-RPC 2.0 batch of ALL notifications...")
        self.test_batch_request(lambda idx: BatchOptions(version=2, notification=True))

        # JSONRPC 1.1 does not support batch requests, but test them for backwards compatibility.
        self.log.info("Testing nonstandard JSON-RPC 1.1 batch request...")
        self.test_batch_request(lambda idx: BatchOptions(version=1))

        self.log.info("Testing nonstandard mixed JSON-RPC 1.1/2.0 batch request...")
        self.test_batch_request(lambda idx: BatchOptions(version=2 if idx % 2 else 1))

        self.log.info("Testing nonstandard batch request without version numbers...")
        self.test_batch_request(lambda idx: BatchOptions())

        self.log.info("Testing nonstandard batch request without version numbers or ids...")
        self.test_batch_request(lambda idx: BatchOptions(notification=True))

        self.log.info("Testing nonstandard jsonrpc 1.0 version number is accepted...")
        self.test_batch_request(lambda idx: BatchOptions(request_fields={"jsonrpc": "1.0"}))

        self.log.info("Testing unrecognized jsonrpc version number is rejected...")
        self.test_batch_request(lambda idx: BatchOptions(
            request_fields={"jsonrpc": "2.1"},
            response_fields={"result": None, "error": {"code": RPC_INVALID_REQUEST, "message": "JSON-RPC version not supported"}}))

    def test_http_status_codes(self):
        self.log.info("Testing HTTP status codes for JSON-RPC 1.1 requests...")
        # OK
        expect_http_rpc_status(200, None,                  self.nodes[0], "getblockhash", [0])
        # Errors
        expect_http_rpc_status(404, RPC_METHOD_NOT_FOUND,  self.nodes[0], "invalidmethod", [])
        expect_http_rpc_status(500, RPC_INVALID_PARAMETER, self.nodes[0], "getblockhash", [42])
        # force-send empty request
        response, status = send_raw_rpc(self.nodes[0], b"")
        assert_equal(response, {"id": None, "result": None, "error": {"code": RPC_PARSE_ERROR, "message": "Parse error"}})
        assert_equal(status, 500)
        # force-send invalidly formatted request
        response, status = send_raw_rpc(self.nodes[0], b"this is bad")
        assert_equal(response, {"id": None, "result": None, "error": {"code": RPC_PARSE_ERROR, "message": "Parse error"}})
        assert_equal(status, 500)

        self.log.info("Testing HTTP status codes for JSON-RPC 2.0 requests...")
        # OK
        expect_http_rpc_status(200, None,                   self.nodes[0], "getblockhash", [0],  2, False)
        # RPC errors and HTTP errors
        expect_http_rpc_status(404, RPC_METHOD_NOT_FOUND,   self.nodes[0], "invalidmethod", [],  2, False)
        expect_http_rpc_status(500, RPC_INVALID_PARAMETER,  self.nodes[0], "getblockhash", [42], 2, False)
        # force-send invalidly formatted requests
        response, status = send_json_rpc(self.nodes[0], {"jsonrpc": 2, "method": "getblockcount"})
        assert_equal(response, {"id": None, "result": None, "error": {"code": RPC_INVALID_REQUEST, "message": "jsonrpc field must be a string"}})
        assert_equal(status, 400)
        response, status = send_json_rpc(self.nodes[0], {"jsonrpc": "3.0", "method": "getblockcount"})
        assert_equal(response, {"id": None, "result": None, "error": {"code": RPC_INVALID_REQUEST, "message": "JSON-RPC version not supported"}})
        assert_equal(status, 400)

        self.log.info("Testing HTTP status codes for JSON-RPC 2.0 notifications...")
        # Not notification: id exists
        response, status = send_json_rpc(self.nodes[0], {"jsonrpc": "2.0", "id": None, "method": "getblockcount"})
        assert_equal(response["result"], 0)
        assert_equal(status, 200)
        # Not notification: JSON 1.1
        expect_http_rpc_status(200, None,                   self.nodes[0], "getblockcount", [],  1)
        # Not notification: has "id" field
        expect_http_rpc_status(200, None,                   self.nodes[0], "getblockcount", [],  2, False)
        block_count = self.nodes[0].getblockcount()
        expect_http_rpc_status(200, None,                   self.nodes[0], "generatetoaddress", [1, "bcrt1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqdku202"],  2, True)
        # The command worked even though there was no response
        assert_equal(block_count + 1, self.nodes[0].getblockcount())
        expect_http_rpc_status(500, RPC_INVALID_ADDRESS_OR_KEY, self.nodes[0], "generatetoaddress", [1, "invalid_address"], 2, True)
        # Sanity check: command was not executed
        assert_equal(block_count + 1, self.nodes[0].getblockcount())

    def test_work_queue_exceeded(self):
        self.log.info("Testing work queue exceeded...")
        self.restart_node(0, ['-rpcworkqueue=1', '-rpcthreads=1'])
        got_exceeded_error = []
        threads = []
        for _ in range(3):
            t = Thread(target=test_work_queue_getblock, args=(self.nodes[0], got_exceeded_error))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def run_test(self):
        self.test_getrpcinfo()
        self.test_batch_request()
        self.test_http_status_codes()


if __name__ == '__main__':
    RPCInterfaceTest().main()
