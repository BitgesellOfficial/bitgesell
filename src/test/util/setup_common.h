// Copyright (c) 2015-2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_TEST_UTIL_SETUP_COMMON_H
#define BGL_TEST_UTIL_SETUP_COMMON_H

#include <chainparamsbase.h>
#include <common/args.h>
#include <key.h>
#include <node/caches.h>
#include <node/context.h>
#include <primitives/transaction.h>
#include <pubkey.h>
#include <random.h>
#include <stdexcept>
#include <util/chaintype.h>
#include <util/check.h>
#include <util/fs.h>
#include <util/string.h>
#include <util/vector.h>

#include <functional>
#include <type_traits>
#include <vector>

class CFeeRate;
class Chainstate;

/** This is connected to the logger. Can be used to redirect logs to any other log */
extern const std::function<void(const std::string&)> G_TEST_LOG_FUN;

/** Retrieve the command line arguments. */
extern const std::function<std::vector<const char*>()> G_TEST_COMMAND_LINE_ARGUMENTS;

// Enable BOOST_CHECK_EQUAL for enum class types
namespace std {
template <typename T>
std::ostream& operator<<(typename std::enable_if<std::is_enum<T>::value, std::ostream>::type& stream, const T& e)
{
    return stream << static_cast<typename std::underlying_type<T>::type>(e);
}
} // namespace std

/**
 * This global and the helpers that use it are not thread-safe.
 *
 * If thread-safety is needed, the global could be made thread_local (given
 * that thread_local is supported on all architectures we support) or a
 * per-thread instance could be used in the multi-threaded test.
 */
extern FastRandomContext g_insecure_rand_ctx;

/**
 * Flag to make GetRand in random.h return the same number
 */
extern bool g_mock_deterministic_tests;

enum class SeedRand {
    ZEROS, //!< Seed with a compile time constant of zeros
    SEED,  //!< Call the Seed() helper
};

/** Seed the given random ctx or use the seed passed in via an environment var */
void Seed(FastRandomContext& ctx);

static inline void SeedInsecureRand(SeedRand seed = SeedRand::SEED)
{
    if (seed == SeedRand::ZEROS) {
        g_insecure_rand_ctx = FastRandomContext(/*fDeterministic=*/true);
    } else {
        Seed(g_insecure_rand_ctx);
    }
}

static constexpr CAmount CENT{1000000};

/** Basic testing setup.
 * This just configures logging, data dir and chain parameters.
 */
struct BasicTestingSetup {
    node::NodeContext m_node; // keep as first member to be destructed last

    explicit BasicTestingSetup(const ChainType chainType = ChainType::MAIN, const std::vector<const char*>& extra_args = {});
    ~BasicTestingSetup();

    const fs::path m_path_root;
    ArgsManager m_args;
};

/** Testing setup that performs all steps up until right before
 * ChainstateManager gets initialized. Meant for testing ChainstateManager
 * initialization behaviour.
 */
struct ChainTestingSetup : public BasicTestingSetup {
    node::CacheSizes m_cache_sizes{};
    bool m_coins_db_in_memory{true};
    bool m_block_tree_db_in_memory{true};

    explicit ChainTestingSetup(const ChainType chainType = ChainType::MAIN, const std::vector<const char*>& extra_args = {});
    ~ChainTestingSetup();

    // Supplies a chainstate, if one is needed
    void LoadVerifyActivateChainstate();
};

/** Testing setup that configures a complete environment.
 */
struct TestingSetup : public ChainTestingSetup {
    explicit TestingSetup(
        const ChainType chainType = ChainType::MAIN,
        const std::vector<const char*>& extra_args = {},
        const bool coins_db_in_memory = true,
        const bool block_tree_db_in_memory = true);
};

/** Identical to TestingSetup, but chain set to regtest */
struct RegTestingSetup : public TestingSetup {
    RegTestingSetup()
        : TestingSetup{ChainType::REGTEST} {}
};

class CBlock;
struct CMutableTransaction;
class CScript;

/**
 * Testing fixture that pre-creates a 100-block REGTEST-mode block chain
 */
struct TestChain100Setup : public TestingSetup {
    TestChain100Setup(
        const ChainType chain_type = ChainType::REGTEST,
        const std::vector<const char*>& extra_args = {},
        const bool coins_db_in_memory = true,
        const bool block_tree_db_in_memory = true);

    /**
     * Create a new block with just given transactions, coinbase paying to
     * scriptPubKey, and try to add it to the current chain.
     * If no chainstate is specified, default to the active.
     */
    CBlock CreateAndProcessBlock(const std::vector<CMutableTransaction>& txns,
                                 const CScript& scriptPubKey,
                                 Chainstate* chainstate = nullptr);

    /**
     * Create a new block with just given transactions, coinbase paying to
     * scriptPubKey.
     */
    CBlock CreateBlock(
        const std::vector<CMutableTransaction>& txns,
        const CScript& scriptPubKey,
        Chainstate& chainstate);

    //! Mine a series of new blocks on the active chain.
    void mineBlocks(int num_blocks);

    /**
     * Create a transaction and submit to the mempool.
     *
     * @param input_transaction  The transaction to spend
     * @param input_vout         The vout to spend from the input_transaction
     * @param input_height       The height of the block that included the input_transaction
     * @param input_signing_key  The key to spend the input_transaction
     * @param output_destination Where to send the output
     * @param output_amount      How much to send
     * @param submit             Whether or not to submit to mempool
     */
    CMutableTransaction CreateValidMempoolTransaction(CTransactionRef input_transaction,
                                                      int input_vout,
                                                      int input_height,
                                                      CKey input_signing_key,
                                                      CScript output_destination,
                                                      CAmount output_amount = CAmount(1 * COIN),
                                                      bool submit = true);

    /** Create transactions spending from m_coinbase_txns. These transactions will only spend coins
     * that exist in the current chain, but may be premature coinbase spends, have missing
     * signatures, or violate some other consensus rules. They should only be used for testing
     * mempool consistency. All transactions will have some random number of inputs and outputs
     * (between 1 and 24). Transactions may or may not be dependent upon each other; if dependencies
     * exit, every parent will always be somewhere in the list before the child so each transaction
     * can be submitted in the same order they appear in the list.
     * @param[in]   submit      When true, submit transactions to the mempool.
     *                          When false, return them but don't submit them.
     * @returns A vector of transactions that can be submitted to the mempool.
     */
    std::vector<CTransactionRef> PopulateMempool(FastRandomContext& det_rand, size_t num_transactions, bool submit);

    /** Mock the mempool minimum feerate by adding a transaction and calling TrimToSize(0),
     * simulating the mempool "reaching capacity" and evicting by descendant feerate.  Note that
     * this clears the mempool, and the new minimum feerate will depend on the maximum feerate of
     * transactions removed, so this must be called while the mempool is empty.
     *
     * @param target_feerate    The new mempool minimum feerate after this function returns.
     *                          Must be above max(incremental feerate, min relay feerate),
     *                          or 1sat/vB with default settings.
     */
    void MockMempoolMinFee(const CFeeRate& target_feerate);

    std::vector<CTransactionRef> m_coinbase_txns; // For convenience, coinbase transactions
    CKey coinbaseKey; // private/public key needed to spend coinbase transactions
};

/**
 * Make a test setup that has disk access to the debug.log file disabled. Can
 * be used in "hot loops", for example fuzzing or benchmarking.
 */
template <class T = const BasicTestingSetup>
std::unique_ptr<T> MakeNoLogFileContext(const ChainType chain_type = ChainType::REGTEST, const std::vector<const char*>& extra_args = {})
{
    const std::vector<const char*> arguments = Cat(
        {
            "-nodebuglogfile",
            "-nodebug",
        },
        extra_args);

    return std::make_unique<T>(chain_type, arguments);
}

CBlock getBlock13b8a();

// define an implicit conversion here so that uint256 may be used directly in BOOST_CHECK_*
std::ostream& operator<<(std::ostream& os, const uint256& num);

/**
 * BOOST_CHECK_EXCEPTION predicates to check the specific validation error.
 * Use as
 * BOOST_CHECK_EXCEPTION(code that throws, exception type, HasReason("foo"));
 */
class HasReason
{
public:
    explicit HasReason(const std::string& reason) : m_reason(reason) {}
    bool operator()(const std::exception& e) const
    {
        return std::string(e.what()).find(m_reason) != std::string::npos;
    };

private:
    const std::string m_reason;
};

#endif // BGL_TEST_UTIL_SETUP_COMMON_H
