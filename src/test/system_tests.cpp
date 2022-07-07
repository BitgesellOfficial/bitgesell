// Copyright (c) 2019-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.
//
#include <test/util/setup_common.h>
#include <util/system.h>
#include <univalue.h>

#ifdef ENABLE_EXTERNAL_SIGNER
#if defined(WIN32) && !defined(__kernel_entry)
// A workaround for boost 1.71 incompatibility with mingw-w64 compiler.
// For details see https://github.com/bitcoin/bitcoin/pull/22348.
#define __kernel_entry
#endif
#include <boost/process.hpp>
#endif // ENABLE_EXTERNAL_SIGNER

#include <boost/test/unit_test.hpp>

BOOST_FIXTURE_TEST_SUITE(system_tests, BasicTestingSetup)

// At least one test is required (in case ENABLE_EXTERNAL_SIGNER is not defined).
// Workaround for https://github.com/bitcoin/bitcoin/issues/19128
BOOST_AUTO_TEST_CASE(dummy)
{
    BOOST_CHECK(true);
}

#ifdef ENABLE_EXTERNAL_SIGNER

bool checkMessage(const std::runtime_error& ex)
{
    // On Linux & Mac: "No such file or directory"
    // On Windows: "The system cannot find the file specified."
    const std::string what(ex.what());
    BOOST_CHECK(what.find("file") != std::string::npos);
    return true;
}

bool checkMessageStdErr(const std::runtime_error& ex)
{
    const std::string what(ex.what());
    BOOST_CHECK(what.find("RunCommandParseJSON error:") != std::string::npos);
    return checkMessage(ex);
}

BOOST_AUTO_TEST_CASE(run_command)
{
    {
        const UniValue result = RunCommandParseJSON("");
        BOOST_CHECK(result.isNull());
    }
    {
#ifdef WIN32
        const UniValue result = RunCommandParseJSON("cmd.exe /c echo {\"success\": true}");
#else
        const UniValue result = RunCommandParseJSON("echo \"{\"success\": true}\"");
#endif
        BOOST_CHECK(result.isObject());
        const UniValue& success = find_value(result, "success");
        BOOST_CHECK(!success.isNull());
        BOOST_CHECK_EQUAL(success.getBool(), true);
    }
    {
        // An invalid command is handled by Boost
        BOOST_CHECK_EXCEPTION(RunCommandParseJSON("invalid_command"), boost::process::process_error, checkMessage); // Command failed
    }
    {
        // Return non-zero exit code, no output to stderr
#ifdef WIN32
        const std::string command{"cmd.exe /c call"};
#else
        const std::string command{"false"};
#endif
        BOOST_CHECK_EXCEPTION(RunCommandParseJSON(command), std::runtime_error, [&](const std::runtime_error& e) {
            BOOST_CHECK(std::string(e.what()).find(strprintf("RunCommandParseJSON error: process(%s) returned 1: \n", command)) != std::string::npos);
            return true;
        });
    }
    {
        // Return non-zero exit code, with error message for stderr
        BOOST_CHECK_EXCEPTION(RunCommandParseJSON("ls nosuchfile"), std::runtime_error, checkMessageStdErr);
    }
    {
        BOOST_REQUIRE_THROW(RunCommandParseJSON("echo \"{\""), std::runtime_error); // Unable to parse JSON
    }
    // Test std::in, except for Windows
#ifndef WIN32
    {
        const UniValue result = RunCommandParseJSON("cat", "{\"success\": true}");
        BOOST_CHECK(result.isObject());
        const UniValue& success = find_value(result, "success");
        BOOST_CHECK(!success.isNull());
        BOOST_CHECK_EQUAL(success.getBool(), true);
    }
#endif
}
#endif // ENABLE_EXTERNAL_SIGNER

BOOST_AUTO_TEST_SUITE_END()
