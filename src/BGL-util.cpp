// Copyright (c) 2009-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#if defined(HAVE_CONFIG_H)
#include <config/BGL-config.h>
#endif

#include <arith_uint256.h>
#include <chain.h>
#include <chainparams.h>
#include <chainparamsbase.h>
#include <clientversion.h>
#include <core_io.h>
#include <streams.h>
#include <util/system.h>
#include <util/translation.h>

#include <atomic>
#include <cstdio>
#include <functional>
#include <memory>
#include <thread>

#include <boost/algorithm/string.hpp>

static const int CONTINUE_EXECUTION=-1;

const std::function<std::string(const char*)> G_TRANSLATION_FUN = nullptr;

static void SetupBGLUtilArgs(ArgsManager &argsman)
{
    SetupHelpOptions(argsman);

    argsman.AddArg("-version", "Print version and exit", ArgsManager::ALLOW_ANY, OptionsCategory::OPTIONS);

    argsman.AddCommand("grind", "Perform proof of work on hex header string");

    SetupChainParamsBaseOptions(argsman);
}

// This function returns either one of EXIT_ codes when it's expected to stop the process or
// CONTINUE_EXECUTION when it's expected to continue further.
static int AppInitUtil(ArgsManager& args, int argc, char* argv[])
{
    SetupBGLUtilArgs(gArgs);
    std::string error;
    if (!args.ParseParameters(argc, argv, error)) {
        tfm::format(std::cerr, "Error parsing command line arguments: %s\n", error);
        return EXIT_FAILURE;
    }

    if (HelpRequested(args) || args.IsArgSet("-version")) {
        // First part of help message is specific to this utility
        std::string strUsage = PACKAGE_NAME " BGL-util utility version " + FormatFullVersion() + "\n";
        if (!args.IsArgSet("-version")) {
            strUsage += "\n"
                "Usage:  BGL-util [options] [commands]  Do stuff\n";
            strUsage += "\n" + args.GetHelpMessage();
        }

        tfm::format(std::cout, "%s", strUsage);

        if (argc < 2) {
            tfm::format(std::cerr, "Error: too few parameters\n");
            return EXIT_FAILURE;
        }
        return EXIT_SUCCESS;
    }


    // Check for chain settings (Params() calls are only valid after this clause)
    try {
        SelectParams(args.GetChainName());
    } catch (const std::exception& e) {
        tfm::format(std::cerr, "Error: %s\n", e.what());
        return EXIT_FAILURE;
    }

    return CONTINUE_EXECUTION;
}

static void grind_task(uint32_t nBits, CBlockHeader& header_orig, uint32_t offset, uint32_t step, std::atomic<bool>& found)
{
    arith_uint256 target;
    bool neg, over;
    target.SetCompact(nBits, &neg, &over);
    if (target == 0 || neg || over) return;
    CBlockHeader header = header_orig; // working copy
    header.nNonce = offset;

    uint32_t finish = std::numeric_limits<uint32_t>::max() - step;
    finish = finish - (finish % step) + offset;

    while (!found && header.nNonce < finish) {
        const uint32_t next = (finish - header.nNonce < 5000*step) ? finish : header.nNonce + 5000*step;
        do {
            if (UintToArith256(header.GetHash()) <= target) {
                if (!found.exchange(true)) {
                    header_orig.nNonce = header.nNonce;
                }
                return;
            }
            header.nNonce += step;
        } while(header.nNonce != next);
    }
}

static int Grind(const std::vector<std::string>& args, std::string& strPrint)
{
    if (argc != 1) {
        strPrint = "Must specify block header to grind";
        return 1;
    }

    CBlockHeader header;
    if (!DecodeHexBlockHeader(header, argv[0])) {
        strPrint = "Could not decode block header";
        return 1;
    }

    uint32_t nBits = header.nBits;
    std::atomic<bool> found{false};

    std::vector<std::thread> threads;
    int n_tasks = std::max(1u, std::thread::hardware_concurrency());
    for (int i = 0; i < n_tasks; ++i) {
        threads.emplace_back( grind_task, nBits, std::ref(header), i, n_tasks, std::ref(found) );
    }
    for (auto& t : threads) {
        t.join();
    }
    if (!found) {
        strPrint = "Could not satisfy difficulty target";
        return 1;
    }

    CDataStream ss(SER_NETWORK, PROTOCOL_VERSION);
    ss << header;
    strPrint = HexStr(ss);
    return 0;
}

static int CommandLineUtil(int argc, char* argv[])
{
    if (argc <= 1) return 1;

    std::string strPrint;
    int nRet = 0;

    try {
        while (argc > 1 && IsSwitchChar(argv[1][0]) && (argv[1][1] != 0)) {
            --argc;
            ++argv;
        }

        char* command = argv[1];
        if (strcmp(command, "grind") == 0) {
            nRet = Grind(argc-2, argv+2, strPrint);
        } else {
            strPrint = strprintf("Unknown command %s", command);
            nRet = 1;
        }
    }
    catch (const std::exception& e) {
        strPrint = std::string("error: ") + e.what();
        nRet = EXIT_FAILURE;
    }
    catch (...) {
        PrintExceptionContinue(nullptr, "CommandLineUtil()");
        throw;
    }

    if (strPrint != "") {
        tfm::format(nRet == 0 ? std::cout : std::cerr, "%s\n", strPrint);
    }
    return nRet;
}

#ifdef WIN32
// Export main() and ensure working ASLR on Windows.
// Exporting a symbol will prevent the linker from stripping
// the .reloc section from the binary, which is a requirement
// for ASLR. This is a temporary workaround until a fixed
// version of binutils is used for releases.
__declspec(dllexport) int main(int argc, char* argv[])
#else
int main(int argc, char* argv[])
#endif
{
    ArgsManager& args = gArgs;
    SetupEnvironment();

    try {
        int ret = AppInitUtil(args, argc, argv);
        if (ret != CONTINUE_EXECUTION) {
            return ret;
        }
    } catch (const std::exception& e) {
        PrintExceptionContinue(&e, "AppInitUtil()");
        return EXIT_FAILURE;
    } catch (...) {
        PrintExceptionContinue(nullptr, "AppInitUtil()");
        return EXIT_FAILURE;
    }

    const auto cmd = args.GetCommand();
    if (!cmd) {
        tfm::format(std::cerr, "Error: must specify a command\n");
        return EXIT_FAILURE;
    }

    int ret = EXIT_FAILURE;
    try {
        ret = CommandLineUtil(argc, argv);
    }
    catch (const std::exception& e) {
        PrintExceptionContinue(&e, "CommandLineUtil()");
    } catch (...) {
        PrintExceptionContinue(nullptr, "CommandLineUtil()");
    }
    return ret;
}
