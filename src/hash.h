// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_HASH_H
#define BGL_HASH_H

#include <attributes.h>
#include <crypto/common.h>
#include <crypto/ripemd160.h>
#include <crypto/sha256.h>
#include <prevector.h>
#include <serialize.h>
#include <uint256.h>

#include <string>
#include <vector>

#include "logging.h"

extern "C" {
#include <crypto/sha3/sha3.h>
}

typedef uint256 ChainCode;

/** A hasher class for Bitcoin's 256-bit hash (double SHA-256). */
class CHash256 {
private:
    CSHA256 sha;
public:
    static const size_t OUTPUT_SIZE = CSHA256::OUTPUT_SIZE;

    void Finalize(Span<unsigned char> output) {
        assert(output.size() == OUTPUT_SIZE);
        unsigned char buf[CSHA256::OUTPUT_SIZE];
        sha.Finalize(buf);
        sha.Reset().Write(buf, CSHA256::OUTPUT_SIZE).Finalize(output.data());
    }

    CHash256& Write(Span<const unsigned char> input) {
        sha.Write(input.data(), input.size());
        return *this;
    }

    CHash256& Reset() {
        sha.Reset();
        return *this;
    }
};

/** A hasher class for BGL's 256-bit hash (single SHA-256). Used for tx ids/hashes */
class CHash256Single {
private:
    CSHA256 sha;
public:
    static const size_t OUTPUT_SIZE = CSHA256::OUTPUT_SIZE;

    void Finalize(unsigned char hash[OUTPUT_SIZE]) {
        sha.Finalize(hash);
    }

    CHash256Single& Write(Span<const std::byte> input) {
        sha.Write(UCharCast(input.data()), input.size());
        return *this;
    }

    CHash256Single& Write(const unsigned char *data, size_t len) {
        sha.Write(data, len);
        return *this;
    }

    CHash256Single& Reset() {
        sha.Reset();
        return *this;
    }
};

/** A SHA3 hasher class specifically for blocks and transactions of BGL. */
class CHash256Keccak {
private:
    sha3_context sha3context;
public:
    static const size_t OUTPUT_SIZE = CSHA256::OUTPUT_SIZE;

    CHash256Keccak() {
        sha3_Init256(&sha3context);
        sha3_SetFlags(&sha3context, SHA3_FLAGS_KECCAK);
    }

    void Finalize(unsigned char hash[OUTPUT_SIZE]) {
        void const *buf;
        buf = sha3_Finalize(&sha3context);

        for (int i = 0; i < 32; i++)
        {
            hash[i] = ((const unsigned char *) buf)[i];
        }
    }

    CHash256Keccak& Write(const unsigned char *data, size_t len) {
        sha3_Update(&sha3context, data, len);
        return *this;
    }

    CHash256Keccak& Reset() {
        sha3_Init256(&sha3context);
        return *this;
    }
};

/** A hasher class for BGL's 160-bit hash (SHA-256 + RIPEMD-160). */
class CHash160 {
private:
    CSHA256 sha;
public:
    static const size_t OUTPUT_SIZE = CRIPEMD160::OUTPUT_SIZE;

    void Finalize(Span<unsigned char> output) {
        assert(output.size() == OUTPUT_SIZE);
        unsigned char buf[CSHA256::OUTPUT_SIZE];
        sha.Finalize(buf);
        CRIPEMD160().Write(buf, CSHA256::OUTPUT_SIZE).Finalize(output.data());
    }

    CHash160& Write(Span<const unsigned char> input) {
        sha.Write(input.data(), input.size());
        return *this;
    }

    CHash160& Reset() {
        sha.Reset();
        return *this;
    }
};

/** Compute the 256-bit hash of an object. */
template<typename T>
inline uint256 Hash(const T& in1)
{
    uint256 result;
    CHash256().Write(MakeUCharSpan(in1)).Finalize(result);
    return result;
}

/** Compute the 256-bit hash of the concatenation of two objects. */
template<typename T1, typename T2>
inline uint256 Hash(const T1& in1, const T2& in2) {
    uint256 result;
    CHash256().Write(MakeUCharSpan(in1)).Write(MakeUCharSpan(in2)).Finalize(result);
    return result;
}

/** Compute the 160-bit hash an object. */
template<typename T1>
inline uint160 Hash160(const T1& in1)
{
    uint160 result;
    CHash160().Write(MakeUCharSpan(in1)).Finalize(result);
    return result;
}

/** A writer stream (for serialization) that computes a 256-bit Keccak hash. */
class CHashWriterKeccak
{
private:
    CHash256Keccak ctx;

    const int nType;
    const int nVersion;
public:

    CHashWriterKeccak(int nTypeIn, int nVersionIn) : nType(nTypeIn), nVersion(nVersionIn) {}

    int GetType() const { return nType; }
    int GetVersion() const { return nVersion; }

    void write(Span<const std::byte> src)
    {
        ctx.Write(UCharCast(src.data()), src.size());
    }

    /** Compute the double-SHA256 hash of all data written to this object.
     *
     * Invalidates this object.
     */
    uint256 GetHash() {
        uint256 result;
        ctx.Finalize((unsigned char*)&result);
        return result;
    }

    /** Compute the SHA256 hash of all data written to this object.
     *
     * Invalidates this object.
     */
    //uint256 GetSHA256() {
    //    uint256 result;
    //    ctx.Finalize(result.begin());
    //    return result;
    //}

    /**
     * Returns the first 64 bits from the resulting hash.
     */
    inline uint64_t GetCheapHash() {
        unsigned char result[CHash256::OUTPUT_SIZE];
        ctx.Finalize(result);
        return ReadLE64(result);
    }

    template<typename T>
    CHashWriterKeccak& operator<<(const T& obj) {
        // Serialize to this stream
        ::Serialize(*this, obj);
        return (*this);
    }
};


class CHashWriterSHA256
{
private:
    CHash256Single ctx;

    const int nType;
    const int nVersion;
public:

    CHashWriterSHA256(int nTypeIn, int nVersionIn) : nType(nTypeIn), nVersion(nVersionIn) {}

    int GetVersion() const { return nVersion; }

    void write(Span<const std::byte> src)
    {
        ctx.Write(src);
    }

    /** Compute the double-SHA256 hash of all data written to this object.
     *
     * Invalidates this object.
     */
    uint256 GetHash() {
        uint256 result;
        ctx.Finalize(result.begin());
        ctx.Reset().Write(result.begin(), CSHA256::OUTPUT_SIZE).Finalize(result.begin());
        return result;
    }
//    uint256 GetHash() {
//        uint256 result;
//        ctx.Finalize(result.begin());
//        return result;
//    }

    /** Compute the SHA256 hash of all data written to this object.
     *
     * Invalidates this object.
     */
    uint256 GetSHA256() {
        uint256 result;
        ctx.Finalize(result.begin());
        return result;
    }

    /**
     * Returns the first 64 bits from the resulting hash.
     */
    inline uint64_t GetCheapHash() {
        unsigned char result[CHash256::OUTPUT_SIZE];
        ctx.Finalize(result);
        return ReadLE64(result);
    }

    template<typename T>
    CHashWriterSHA256& operator<<(const T& obj) {
        // Serialize to this stream
        ::Serialize(*this, obj);
        return (*this);
    }
};

/** Reads data from an underlying stream, while hashing the read data. */
template<typename Source>
class CHashVerifier : public CHashWriterKeccak
{
private:
    Source* source;

public:
    explicit CHashVerifier(Source* source_) : CHashWriterKeccak(source_->GetType(), source_->GetVersion()), source(source_) {}

    void read(Span<std::byte> dst)
    {
        source->read(dst);
        this->write(dst);
    }

    void ignore(size_t nSize)
    {
        std::byte data[1024];
        while (nSize > 0) {
            size_t now = std::min<size_t>(nSize, 1024);
            read({data, now});
            nSize -= now;
        }
    }

    template<typename T>
    CHashVerifier<Source>& operator>>(T&& obj)
    {
        // Unserialize from this stream
        ::Unserialize(*this, obj);
        return (*this);
    }
};

/** Writes data to an underlying source stream, while hashing the written data. */
template <typename Source>
class HashedSourceWriter : public CHashWriterKeccak
{
private:
    Source& m_source;

public:
    explicit HashedSourceWriter(Source& source LIFETIMEBOUND) : CHashWriterKeccak(source.GetType(), source.GetVersion()), m_source{source} {}

    void write(Span<const std::byte> src)
    {
        m_source.write(src);
        CHashWriterKeccak::write(src);
    }

    template <typename T>
    HashedSourceWriter& operator<<(const T& obj)
    {
        ::Serialize(*this, obj);
        return *this;
    }
};


/** Compute the 256-bit hash of an object's serialization. */
template<typename T>
uint256 SerializeHashKeccak(const T& obj, int nType=SER_GETHASH, int nVersion=PROTOCOL_VERSION)
{
    CHashWriterKeccak ss(nType, nVersion);
    ss << obj;
    return ss.GetHash();
}

template<typename T>
uint256 SerializeHashSHA256(const T& obj, int nType=SER_GETHASH, int nVersion=PROTOCOL_VERSION)
{
    CHashWriterSHA256 ss(nType, nVersion);
    ss << obj;
    return ss.GetSHA256();
}

/** Single-SHA256 a 32-byte input (represented as uint256). */
[[nodiscard]] uint256 SHA256Uint256(const uint256& input);

unsigned int MurmurHash3(unsigned int nHashSeed, Span<const unsigned char> vDataToHash);

void BIP32Hash(const ChainCode &chainCode, unsigned int nChild, unsigned char header, const unsigned char data[32], unsigned char output[64]);

/** Return a CHashWriter primed for tagged hashes (as specified in BIP 340).
 *
 * The returned object will have SHA256(tag) written to it twice (= 64 bytes).
 * A tagged hash can be computed by feeding the message into this object, and
 * then calling CHashWriter::GetSHA256().
 */
CHashWriterSHA256 TaggedHash(const std::string& tag);

/** Compute the 160-bit RIPEMD-160 hash of an array. */
inline uint160 RIPEMD160(Span<const unsigned char> data)
{
    uint160 result;
    CRIPEMD160().Write(data.data(), data.size()).Finalize(result.begin());
    return result;
}

#endif // BGL_HASH_H
