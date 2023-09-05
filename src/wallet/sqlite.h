// Copyright (c) 2020-2021 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_WALLET_SQLITE_H
#define BGL_WALLET_SQLITE_H

#include <wallet/db.h>

#include <sqlite3.h>

struct bilingual_str;

namespace wallet {
class SQLiteDatabase;

/** RAII class that provides a database cursor */
class SQLiteCursor : public DatabaseCursor
{
public:
    sqlite3_stmt* m_cursor_stmt{nullptr};
    // Copies of the prefix things for the prefix cursor.
    // Prevents SQLite from accessing temp variables for the prefix things.
    std::vector<std::byte> m_prefix_range_start;
    std::vector<std::byte> m_prefix_range_end;

    explicit SQLiteCursor() {}
    explicit SQLiteCursor(std::vector<std::byte> start_range, std::vector<std::byte> end_range)
        : m_prefix_range_start(std::move(start_range)),
        m_prefix_range_end(std::move(end_range))
    {}
    ~SQLiteCursor() override;

    Status Next(DataStream& key, DataStream& value) override;
};

/** RAII class that provides access to a WalletDatabase */
class SQLiteBatch : public DatabaseBatch
{
private:
    SQLiteDatabase& m_database;

    bool m_cursor_init = false;

    sqlite3_stmt* m_read_stmt{nullptr};
    sqlite3_stmt* m_insert_stmt{nullptr};
    sqlite3_stmt* m_overwrite_stmt{nullptr};
    sqlite3_stmt* m_delete_stmt{nullptr};
    sqlite3_stmt* m_delete_prefix_stmt{nullptr};

    void SetupSQLStatements();
    bool ExecStatement(sqlite3_stmt* stmt, Span<const std::byte> blob);

    bool ReadKey(DataStream&& key, DataStream& value) override;
    bool WriteKey(DataStream&& key, DataStream&& value, bool overwrite = true) override;
    bool EraseKey(DataStream&& key) override;
    bool HasKey(DataStream&& key) override;
    bool ErasePrefix(Span<const std::byte> prefix) override;

public:
    explicit SQLiteBatch(SQLiteDatabase& database);
    ~SQLiteBatch() override { Close(); }

    /* No-op. See comment on SQLiteDatabase::Flush */
    void Flush() override {}

    void Close() override;

    std::unique_ptr<DatabaseCursor> GetNewCursor() override;
    std::unique_ptr<DatabaseCursor> GetNewPrefixCursor(Span<const std::byte> prefix) override;
    bool TxnBegin() override;
    bool TxnCommit() override;
    bool TxnAbort() override;
};

/** An instance of this class represents one SQLite3 database.
 **/
class SQLiteDatabase : public WalletDatabase
{
private:
    const bool m_mock{false};

    const std::string m_dir_path;

    const std::string m_file_path;

    void Cleanup() noexcept;

public:
    SQLiteDatabase() = delete;

    /** Create DB handle to real database */
    SQLiteDatabase(const fs::path& dir_path, const fs::path& file_path, const DatabaseOptions& options, bool mock = false);

    ~SQLiteDatabase();

    bool Verify(bilingual_str& error);

    /** Open the database if it is not already opened */
    void Open() override;

    /** Close the database */
    void Close() override;

    /* These functions are unused */
    void AddRef() override { assert(false); }
    void RemoveRef() override { assert(false); }

    /** Rewrite the entire database on disk */
    bool Rewrite(const char* skip = nullptr) override;

    /** Back up the entire database to a file.
     */
    bool Backup(const std::string& dest) const override;

    /** No-ops
     *
     * SQLite always flushes everything to the database file after each transaction
     * (each Read/Write/Erase that we do is its own transaction unless we called
     * TxnBegin) so there is no need to have Flush or Periodic Flush.
     *
     * There is no DB env to reload, so ReloadDbEnv has nothing to do
     */
    void Flush() override {}
    bool PeriodicFlush() override { return false; }
    void ReloadDbEnv() override {}

    void IncrementUpdateCounter() override { ++nUpdateCounter; }

    std::string Filename() override { return m_file_path; }
    std::string Format() override { return "sqlite"; }

    /** Make a SQLiteBatch connected to this database */
    std::unique_ptr<DatabaseBatch> MakeBatch(bool flush_on_close = true) override;

    sqlite3* m_db{nullptr};
    bool m_use_unsafe_sync;
};

std::unique_ptr<SQLiteDatabase> MakeSQLiteDatabase(const fs::path& path, const DatabaseOptions& options, DatabaseStatus& status, bilingual_str& error);

std::string SQLiteDatabaseVersion();
} // namespace wallet

#endif // BGL_WALLET_SQLITE_H
