// Copyright (c) 2021-2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_WALLET_TEST_UTIL_H
#define BGL_WALLET_TEST_UTIL_H

#include <script/standard.h>
#include <wallet/db.h>

#include <memory>

class ArgsManager;
class CChain;
class CKey;
enum class OutputType;
namespace interfaces {
class Chain;
} // namespace interfaces

namespace wallet {
class CWallet;
struct DatabaseOptions;
class WalletDatabase;

std::unique_ptr<CWallet> CreateSyncedWallet(interfaces::Chain& chain, CChain& cchain, const CKey& key);

// Creates a copy of the provided database
std::unique_ptr<WalletDatabase> DuplicateMockDatabase(WalletDatabase& database, DatabaseOptions& options);

/** Returns a new encoded destination from the wallet (hardcoded to BECH32) */
std::string getnewaddress(CWallet& w);
/** Returns a new destination, of an specific type, from the wallet */
CTxDestination getNewDestination(CWallet& w, OutputType output_type);

class MockableCursor: public DatabaseCursor
{
public:
    std::map<SerializeData, SerializeData>::const_iterator m_cursor;
    std::map<SerializeData, SerializeData>::const_iterator m_cursor_end;
    bool m_pass;

    explicit MockableCursor(const std::map<SerializeData, SerializeData>& records, bool pass) : m_cursor(records.begin()), m_cursor_end(records.end()), m_pass(pass) {}
    ~MockableCursor() {}

    Status Next(DataStream& key, DataStream& value) override;
};

class MockableBatch : public DatabaseBatch
{
private:
    std::map<SerializeData, SerializeData>& m_records;
    bool m_pass;

    bool ReadKey(DataStream&& key, DataStream& value) override;
    bool WriteKey(DataStream&& key, DataStream&& value, bool overwrite=true) override;
    bool EraseKey(DataStream&& key) override;
    bool HasKey(DataStream&& key) override;
    bool ErasePrefix(Span<const std::byte> prefix) override;

public:
    explicit MockableBatch(std::map<SerializeData, SerializeData>& records, bool pass) : m_records(records), m_pass(pass) {}
    ~MockableBatch() {}

    void Flush() override {}
    void Close() override {}

    std::unique_ptr<DatabaseCursor> GetNewCursor() override
    {
        return std::make_unique<MockableCursor>(m_records, m_pass);
    }
    bool TxnBegin() override { return m_pass; }
    bool TxnCommit() override { return m_pass; }
    bool TxnAbort() override { return m_pass; }
};

/** A WalletDatabase whose contents and return values can be modified as needed for testing
 **/
class MockableDatabase : public WalletDatabase
{
public:
    std::map<SerializeData, SerializeData> m_records;
    bool m_pass{true};

    MockableDatabase(std::map<SerializeData, SerializeData> records = {}) : WalletDatabase(), m_records(records) {}
    ~MockableDatabase() {};

    void Open() override {}
    void AddRef() override {}
    void RemoveRef() override {}

    bool Rewrite(const char* pszSkip=nullptr) override { return m_pass; }
    bool Backup(const std::string& strDest) const override { return m_pass; }
    void Flush() override {}
    void Close() override {}
    bool PeriodicFlush() override { return m_pass; }
    void IncrementUpdateCounter() override {}
    void ReloadDbEnv() override {}

    std::string Filename() override { return "mockable"; }
    std::string Format() override { return "mock"; }
    std::unique_ptr<DatabaseBatch> MakeBatch(bool flush_on_close = true) override { return std::make_unique<MockableBatch>(m_records, m_pass); }
};

std::unique_ptr<WalletDatabase> CreateMockableWalletDatabase(std::map<SerializeData, SerializeData> records = {});

MockableDatabase& GetMockableDatabase(CWallet& wallet);
} // namespace wallet

#endif // BGL_WALLET_TEST_UTIL_H