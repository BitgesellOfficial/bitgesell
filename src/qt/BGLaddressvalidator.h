// Copyright (c) 2011-2014 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_QT_BGLADDRESSVALIDATOR_H
#define BGL_QT_BGLADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class BGLAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit BGLAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

/** BGL address widget validator, checks for a valid BGL address.
 */
class BGLAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit BGLAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

#endif // BGL_QT_BGLADDRESSVALIDATOR_H
