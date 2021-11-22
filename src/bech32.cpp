// Copyright (c) 2017, 2021 Pieter Wuille
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <bech32.h>
#include <util/vector.h>

#include <assert.h>
#include <optional>

namespace bech32
{

namespace
{

typedef std::vector<uint8_t> data;

/** The Bech32 and Bech32m character set for encoding. */
const char* CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";

/** The Bech32 and Bech32m character set for decoding. */
const int8_t CHARSET_REV[128] = {
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    15, -1, 10, 17, 21, 20, 26, 30,  7,  5, -1, -1, -1, -1, -1, -1,
    -1, 29, -1, 24, 13, 25,  9,  8, 23, -1, 18, 22, 31, 27, 19, -1,
     1,  0,  3, 16, 11, 28, 12, 14,  6,  4,  2, -1, -1, -1, -1, -1,
    -1, 29, -1, 24, 13, 25,  9,  8, 23, -1, 18, 22, 31, 27, 19, -1,
     1,  0,  3, 16, 11, 28, 12, 14,  6,  4,  2, -1, -1, -1, -1, -1
};

/* Determine the final constant to use for the specified encoding. */
uint32_t EncodingConstant(Encoding encoding) {
    assert(encoding == Encoding::BECH32 || encoding == Encoding::BECH32M);
    return encoding == Encoding::BECH32 ? 1 : 0x2bc830a3;
}

/** This function will compute what 6 5-bit values to XOR into the last 6 input values, in order to
 *  make the checksum 0. These 6 values are packed together in a single 30-bit integer. The higher
 *  bits correspond to earlier values. */
uint32_t PolyMod(const data& v)
{
    // The input is interpreted as a list of coefficients of a polynomial over F = GF(32), with an
    // implicit 1 in front. If the input is [v0,v1,v2,v3,v4], that polynomial is v(x) =
    // 1*x^5 + v0*x^4 + v1*x^3 + v2*x^2 + v3*x + v4. The implicit 1 guarantees that
    // [v0,v1,v2,...] has a distinct checksum from [0,v0,v1,v2,...].

    // The output is a 30-bit integer whose 5-bit groups are the coefficients of the remainder of
    // v(x) mod g(x), where g(x) is the Bech32 generator,
    // x^6 + {29}x^5 + {22}x^4 + {20}x^3 + {21}x^2 + {29}x + {18}. g(x) is chosen in such a way
    // that the resulting code is a BCH code, guaranteeing detection of up to 3 errors within a
    // window of 1023 characters. Among the various possible BCH codes, one was selected to in
    // fact guarantee detection of up to 4 errors within a window of 89 characters.

    // Note that the coefficients are elements of GF(32), here represented as decimal numbers
    // between {}. In this finite field, addition is just XOR of the corresponding numbers. For
    // example, {27} + {13} = {27 ^ 13} = {22}. Multiplication is more complicated, and requires
    // treating the bits of values themselves as coefficients of a polynomial over a smaller field,
    // GF(2), and multiplying those polynomials mod a^5 + a^3 + 1. For example, {5} * {26} =
    // (a^2 + 1) * (a^4 + a^3 + a) = (a^4 + a^3 + a) * a^2 + (a^4 + a^3 + a) = a^6 + a^5 + a^4 + a
    // = a^3 + 1 (mod a^5 + a^3 + 1) = {9}.

    // During the course of the loop below, `c` contains the bitpacked coefficients of the
    // polynomial constructed from just the values of v that were processed so far, mod g(x). In
    // the above example, `c` initially corresponds to 1 mod g(x), and after processing 2 inputs of
    // v, it corresponds to x^2 + v0*x + v1 mod g(x). As 1 mod g(x) = 1, that is the starting value
    // for `c`.

    // The following Sage code constructs the generator used:
    //
    // B = GF(2) # Binary field
    // BP.<b> = B[] # Polynomials over the binary field
    // F_mod = b**5 + b**3 + 1
    // F.<f> = GF(32, modulus=F_mod, repr='int') # GF(32) definition
    // FP.<x> = F[] # Polynomials over GF(32)
    // E_mod = x**2 + F.fetch_int(9)*x + F.fetch_int(23)
    // E.<e> = F.extension(E_mod) # GF(1024) extension field definition
    // for p in divisors(E.order() - 1): # Verify e has order 1023.
    //    assert((e**p == 1) == (p % 1023 == 0))
    // G = lcm([(e**i).minpoly() for i in range(997,1000)])
    // print(G) # Print out the generator
    //
    // It demonstrates that g(x) is the least common multiple of the minimal polynomials
    // of 3 consecutive powers (997,998,999) of a primitive element (e) of GF(1024).
    // That guarantees it is, in fact, the generator of a primitive BCH code with cycle
    // length 1023 and distance 4. See https://en.wikipedia.org/wiki/BCH_code for more details.

    uint32_t c = 1;
    for (const auto v_i : v) {
        // We want to update `c` to correspond to a polynomial with one extra term. If the initial
        // value of `c` consists of the coefficients of c(x) = f(x) mod g(x), we modify it to
        // correspond to c'(x) = (f(x) * x + v_i) mod g(x), where v_i is the next input to
        // process. Simplifying:
        // c'(x) = (f(x) * x + v_i) mod g(x)
        //         ((f(x) mod g(x)) * x + v_i) mod g(x)
        //         (c(x) * x + v_i) mod g(x)
        // If c(x) = c0*x^5 + c1*x^4 + c2*x^3 + c3*x^2 + c4*x + c5, we want to compute
        // c'(x) = (c0*x^5 + c1*x^4 + c2*x^3 + c3*x^2 + c4*x + c5) * x + v_i mod g(x)
        //       = c0*x^6 + c1*x^5 + c2*x^4 + c3*x^3 + c4*x^2 + c5*x + v_i mod g(x)
        //       = c0*(x^6 mod g(x)) + c1*x^5 + c2*x^4 + c3*x^3 + c4*x^2 + c5*x + v_i
        // If we call (x^6 mod g(x)) = k(x), this can be written as
        // c'(x) = (c1*x^5 + c2*x^4 + c3*x^3 + c4*x^2 + c5*x + v_i) + c0*k(x)

        // First, determine the value of c0:
        uint8_t c0 = c >> 25;

        // Then compute c1*x^5 + c2*x^4 + c3*x^3 + c4*x^2 + c5*x + v_i:
        c = ((c & 0x1ffffff) << 5) ^ v_i;

        // Finally, for each set bit n in c0, conditionally add {2^n}k(x). These constants can be
        // computed using the following Sage code (continuing the code above):
        //
        // for i in [1,2,4,8,16]: # Print out {1,2,4,8,16}*(g(x) mod x^6), packed in hex integers.
        //     v = 0
        //     for coef in reversed((F.fetch_int(i)*(G % x**6)).coefficients(sparse=True)):
        //         v = v*32 + coef.integer_representation()
        //     print("0x%x" % v)
        //
        if (c0 & 1)  c ^= 0x3b6a57b2; //     k(x) = {29}x^5 + {22}x^4 + {20}x^3 + {21}x^2 + {29}x + {18}
        if (c0 & 2)  c ^= 0x26508e6d; //  {2}k(x) = {19}x^5 +  {5}x^4 +     x^3 +  {3}x^2 + {19}x + {13}
        if (c0 & 4)  c ^= 0x1ea119fa; //  {4}k(x) = {15}x^5 + {10}x^4 +  {2}x^3 +  {6}x^2 + {15}x + {26}
        if (c0 & 8)  c ^= 0x3d4233dd; //  {8}k(x) = {30}x^5 + {20}x^4 +  {4}x^3 + {12}x^2 + {30}x + {29}
        if (c0 & 16) c ^= 0x2a1462b3; // {16}k(x) = {21}x^5 +     x^4 +  {8}x^3 + {24}x^2 + {21}x + {19}

    }
    return c;
}

/** Convert to lower case. */
inline unsigned char LowerCase(unsigned char c)
{
    return (c >= 'A' && c <= 'Z') ? (c - 'A') + 'a' : c;
}

void push_range(int from, int to, std::vector<int>& vec)
{
    for (int i = from; i < to; i++) {
        vec.push_back(i);
    }
}

/** Return indices of invalid characters in a Bech32 string. */
bool CheckCharacters(const std::string& str, std::vector<int>& errors) {
    bool lower = false, upper = false;
    for (size_t i = 0; i < str.size(); ++i) {
        unsigned char c = str[i];
        if (c >= 'a' && c <= 'z') {
            if (upper) {
                errors.push_back(i);
            } else {
                lower = true;
            }
        } else if (c >= 'A' && c <= 'Z') {
            if (lower) {
                errors.push_back(i);
            } else {
                upper = true;
            }
        } else if (c < 33 || c > 126) {
            errors.push_back(i);
        }
    }
    return errors.empty();
}

/** Expand a HRP for use in checksum computation. */
data ExpandHRP(const std::string& hrp)
{
    data ret;
    ret.reserve(hrp.size() + 90);
    ret.resize(hrp.size() * 2 + 1);
    for (size_t i = 0; i < hrp.size(); ++i) {
        unsigned char c = hrp[i];
        ret[i] = c >> 5;
        ret[i + hrp.size() + 1] = c & 0x1f;
    }
    ret[hrp.size()] = 0;
    return ret;
}

/** Verify a checksum. */
Encoding VerifyChecksum(const std::string& hrp, const data& values)
{
    // PolyMod computes what value to xor into the final values to make the checksum 0. However,
    // if we required that the checksum was 0, it would be the case that appending a 0 to a valid
    // list of values would result in a new valid list. For that reason, Bech32 requires the
    // resulting checksum to be 1 instead. In Bech32m, this constant was amended. See
    // https://gist.github.com/sipa/14c248c288c3880a3b191f978a34508e for details.
    const uint32_t check = PolyMod(Cat(ExpandHRP(hrp), values));
    if (check == EncodingConstant(Encoding::BECH32)) return Encoding::BECH32;
    if (check == EncodingConstant(Encoding::BECH32M)) return Encoding::BECH32M;
    return Encoding::INVALID;
}

/** Create a checksum. */
data CreateChecksum(Encoding encoding, const std::string& hrp, const data& values)
{
    data enc = Cat(ExpandHRP(hrp), values);
    enc.resize(enc.size() + 6); // Append 6 zeroes
    uint32_t mod = PolyMod(enc) ^ EncodingConstant(encoding); // Determine what to XOR into those 6 zeroes.
    data ret(6);
    for (size_t i = 0; i < 6; ++i) {
        // Convert the 5-bit groups in mod to checksum values.
        ret[i] = (mod >> (5 * (5 - i))) & 31;
    }
    return ret;
}

} // namespace

/** Encode a Bech32 or Bech32m string. */
std::string Encode(Encoding encoding, const std::string& hrp, const data& values) {
    // First ensure that the HRP is all lowercase. BIP-173 and BIP350 require an encoder
    // to return a lowercase Bech32/Bech32m string, but if given an uppercase HRP, the
    // result will always be invalid.
    for (const char& c : hrp) assert(c < 'A' || c > 'Z');
    data checksum = CreateChecksum(encoding, hrp, values);
    data combined = Cat(values, checksum);
    std::string ret = hrp + '1';
    ret.reserve(ret.size() + combined.size());
    for (const auto c : combined) {
        ret += CHARSET[c];
    }
    return ret;
}

/** Decode a Bech32 or Bech32m string. */
DecodeResult Decode(const std::string& str) {
    bool lower = false, upper = false;
    for (size_t i = 0; i < str.size(); ++i) {
        unsigned char c = str[i];
        if (c >= 'a' && c <= 'z') lower = true;
        else if (c >= 'A' && c <= 'Z') upper = true;
        else if (c < 33 || c > 126) return {};
    }
    if (lower && upper) return {};
    size_t pos = str.rfind('1');
    if (str.size() > 90 || pos == str.npos || pos == 0 || pos + 7 > str.size()) {
        return {};
    }
    data values(str.size() - 1 - pos);
    for (size_t i = 0; i < str.size() - 1 - pos; ++i) {
        unsigned char c = str[i + pos + 1];
        int8_t rev = CHARSET_REV[c];

        if (rev == -1) {
            return {};
        }
        values[i] = rev;
    }
    std::string hrp;
    for (size_t i = 0; i < pos; ++i) {
        hrp += LowerCase(str[i]);
    }
    Encoding result = VerifyChecksum(hrp, values);
    if (result == Encoding::INVALID) return {};
    return {result, std::move(hrp), data(values.begin(), values.end() - 6)};
}

/** Find index of an incorrect character in a Bech32 string. */
std::string LocateErrors(const std::string& str, std::vector<int>& error_locations) {
    if (str.size() > 90) {
        push_range(90, str.size(), error_locations);
        return "Bech32 string too long";
    }
    if (!CheckCharacters(str, error_locations)){
        return "Invalid character or mixed case";
    }
    size_t pos = str.rfind('1');
    if (pos == str.npos) {
        return "Missing separator";
    }
    if (pos == 0 || pos + 7 > str.size()) {
        error_locations.push_back(pos);
        return "Invalid separator position";
    }
    std::string hrp;
    for (size_t i = 0; i < pos; ++i) {
        hrp += LowerCase(str[i]);
    }

    size_t length = str.size() - 1 - pos; // length of data part
    data values(length);
    for (size_t i = pos + 1; i < str.size(); ++i) {
        unsigned char c = str[i];
        int8_t rev = CHARSET_REV[c];
        if (rev == -1) {
            error_locations.push_back(i);
            return "Invalid Base 32 character";
        }
        values[i - pos - 1] = rev;
    }

    // We attempt error detection with both bech32 and bech32m, and choose the one with the fewest errors
    // We can't simply use the segwit version, because that may be one of the errors
    std::optional<Encoding> error_encoding;
    for (Encoding encoding : {Encoding::BECH32, Encoding::BECH32M}) {
        std::vector<int> possible_errors;
        // Recall that (ExpandHRP(hrp) ++ values) is interpreted as a list of coefficients of a polynomial
        // over GF(32). PolyMod computes the "remainder" of this polynomial modulo the generator G(x).
        uint32_t residue = PolyMod(Cat(ExpandHRP(hrp), values)) ^ EncodingConstant(encoding);

        // All valid codewords should be multiples of G(x), so this remainder (after XORing with the encoding
        // constant) should be 0 - hence 0 indicates there are no errors present.
        if (residue != 0) {
            // If errors are present, our polynomial must be of the form C(x) + E(x) where C is the valid
            // codeword (a multiple of G(x)), and E encodes the errors.
            uint32_t syn = Syndrome(residue);

            // Unpack the three 10-bit syndrome values
            int s0 = syn & 0x3FF;
            int s1 = (syn >> 10) & 0x3FF;
            int s2 = syn >> 20;

            // Get the discrete logs of these values in GF1024 for more efficient computation
            int l_s0 = GF1024_LOG[s0];
            int l_s1 = GF1024_LOG[s1];
            int l_s2 = GF1024_LOG[s2];

            // First, suppose there is only a single error. Then E(x) = e1*x^p1 for some position p1
            // Then s0 = E((e)^997) = e1*(e)^(997*p1) and s1 = E((e)^998) = e1*(e)^(998*p1)
            // Therefore s1/s0 = (e)^p1, and by the same logic, s2/s1 = (e)^p1 too.
            // Hence, s1^2 == s0*s2, which is exactly the condition we check first:
            if (l_s0 != -1 && l_s1 != -1 && l_s2 != -1 && (2 * l_s1 - l_s2 - l_s0 + 2046) % 1023 == 0) {
                // Compute the error position p1 as l_s1 - l_s0 = p1 (mod 1023)
                size_t p1 = (l_s1 - l_s0 + 1023) % 1023; // the +1023 ensures it is positive
                // Now because s0 = e1*(e)^(997*p1), we get e1 = s0/((e)^(997*p1)). Remember that (e)^1023 = 1,
                // so 1/((e)^997) = (e)^(1023-997).
                int l_e1 = l_s0 + (1023 - 997) * p1;
                // Finally, some sanity checks on the result:
                // - The error position should be within the length of the data
                // - e1 should be in GF(32), which implies that e1 = (e)^(33k) for some k (the 31 non-zero elements
                // of GF(32) form an index 33 subgroup of the 1023 non-zero elements of GF(1024)).
                if (p1 < length && !(l_e1 % 33)) {
                    // Polynomials run from highest power to lowest, so the index p1 is from the right.
                    // We don't return e1 because it is dangerous to suggest corrections to the user,
                    // the user should check the address themselves.
                    possible_errors.push_back(str.size() - p1 - 1);
                }
            // Otherwise, suppose there are two errors. Then E(x) = e1*x^p1 + e2*x^p2.
            } else {
                // For all possible first error positions p1
                for (size_t p1 = 0; p1 < length; ++p1) {
                    // We have guessed p1, and want to solve for p2. Recall that E(x) = e1*x^p1 + e2*x^p2, so
                    // s0 = E((e)^997) = e1*(e)^(997^p1) + e2*(e)^(997*p2), and similar for s1 and s2.
                    //
                    // Consider s2 + s1*(e)^p1
                    //          = 2e1*(e)^(999^p1) + e2*(e)^(999*p2) + e2*(e)^(998*p2)*(e)^p1
                    //          = e2*(e)^(999*p2) + e2*(e)^(998*p2)*(e)^p1
                    //    (Because we are working in characteristic 2.)
                    //          = e2*(e)^(998*p2) ((e)^p2 + (e)^p1)
                    //
                    int s2_s1p1 = s2 ^ (s1 == 0 ? 0 : GF1024_EXP[(l_s1 + p1) % 1023]);
                    if (s2_s1p1 == 0) continue;
                    int l_s2_s1p1 = GF1024_LOG[s2_s1p1];

                    // Similarly, s1 + s0*(e)^p1
                    //          = e2*(e)^(997*p2) ((e)^p2 + (e)^p1)
                    int s1_s0p1 = s1 ^ (s0 == 0 ? 0 : GF1024_EXP[(l_s0 + p1) % 1023]);
                    if (s1_s0p1 == 0) continue;
                    int l_s1_s0p1 = GF1024_LOG[s1_s0p1];

                    // So, putting these together, we can compute the second error position as
                    // (e)^p2 = (s2 + s1^p1)/(s1 + s0^p1)
                    // p2 = log((e)^p2)
                    size_t p2 = (l_s2_s1p1 - l_s1_s0p1 + 1023) % 1023;

                    // Sanity checks that p2 is a valid position and not the same as p1
                    if (p2 >= length || p1 == p2) continue;

                    // Now we want to compute the error values e1 and e2.
                    // Similar to above, we compute s1 + s0*(e)^p2
                    //          = e1*(e)^(997*p1) ((e)^p1 + (e)^p2)
                    int s1_s0p2 = s1 ^ (s0 == 0 ? 0 : GF1024_EXP[(l_s0 + p2) % 1023]);
                    if (s1_s0p2 == 0) continue;
                    int l_s1_s0p2 = GF1024_LOG[s1_s0p2];

                    // And compute (the log of) 1/((e)^p1 + (e)^p2))
                    int inv_p1_p2 = 1023 - GF1024_LOG[GF1024_EXP[p1] ^ GF1024_EXP[p2]];

                    // Then (s1 + s0*(e)^p1) * (1/((e)^p1 + (e)^p2)))
                    //         = e2*(e)^(997*p2)
                    // Then recover e2 by dividing by (e)^(997*p2)
                    int l_e2 = l_s1_s0p1 + inv_p1_p2 + (1023 - 997) * p2;
                    // Check that e2 is in GF(32)
                    if (l_e2 % 33) continue;

                    // In the same way, (s1 + s0*(e)^p2) * (1/((e)^p1 + (e)^p2)))
                    //         = e1*(e)^(997*p1)
                    // So recover e1 by dividing by (e)^(997*p1)
                    int l_e1 = l_s1_s0p2 + inv_p1_p2 + (1023 - 997) * p1;
                    // Check that e1 is in GF(32)
                    if (l_e1 % 33) continue;

                    // Again, we do not return e1 or e2 for safety.
                    // Order the error positions from the left of the string and return them
                    if (p1 > p2) {
                        possible_errors.push_back(str.size() - p1 - 1);
                        possible_errors.push_back(str.size() - p2 - 1);
                    } else {
                        possible_errors.push_back(str.size() - p2 - 1);
                        possible_errors.push_back(str.size() - p1 - 1);
                    }
                    break;
                }
            }
        } else {
            // No errors
            error_locations.clear();
            return "";
        }

        if (error_locations.empty() || (!possible_errors.empty() && possible_errors.size() < error_locations.size())) {
            error_locations = std::move(possible_errors);
            if (!error_locations.empty()) error_encoding = encoding;
        }
    }
    return error_encoding == Encoding::BECH32M ? "Invalid Bech32m checksum"
            : error_encoding == Encoding::BECH32 ? "Invalid Bech32 checksum"
            : "Invalid checksum";

}

} // namespace bech32
