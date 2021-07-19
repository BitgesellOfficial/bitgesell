// Copyright (c) 2009-2018 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <qt/test/uritests.h>

#include <qt/guiutil.h>
#include <qt/walletmodel.h>

#include <QUrl>

void URITests::uriTests()
{
    SendCoinsRecipient rv;
    QUrl uri;
    uri.setUrl(QString("BGL:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?req-dontexist="));
    QVERIFY(!GUIUtil::parseBGLURI(uri, &rv));

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?dontexist="));
    QVERIFY(GUIUtil::parseBGLURI(uri, &rv));
    QVERIFY(rv.address == QString("BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L"));
    QVERIFY(rv.label == QString());
    QVERIFY(rv.amount == 0);

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?label=Wikipedia Example Address"));
    QVERIFY(GUIUtil::parseBGLURI(uri, &rv));
    QVERIFY(rv.address == QString("BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L"));
    QVERIFY(rv.label == QString("Wikipedia Example Address"));
    QVERIFY(rv.amount == 0);

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?amount=0.001"));
    QVERIFY(GUIUtil::parseBGLURI(uri, &rv));
    QVERIFY(rv.address == QString("BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L"));
    QVERIFY(rv.label == QString());
    QVERIFY(rv.amount == 100000);

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?amount=1.001"));
    QVERIFY(GUIUtil::parseBGLURI(uri, &rv));
    QVERIFY(rv.address == QString("BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L"));
    QVERIFY(rv.label == QString());
    QVERIFY(rv.amount == 100100000);

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?amount=100&label=Wikipedia Example"));
    QVERIFY(GUIUtil::parseBGLURI(uri, &rv));
    QVERIFY(rv.address == QString("BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L"));
    QVERIFY(rv.amount == 10000000000LL);
    QVERIFY(rv.label == QString("Wikipedia Example"));

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?message=Wikipedia Example Address"));
    QVERIFY(GUIUtil::parseBGLURI(uri, &rv));
    QVERIFY(rv.address == QString("BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L"));
    QVERIFY(rv.label == QString());

    QVERIFY(GUIUtil::parseBGLURI("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?message=Wikipedia Example Address", &rv));
    QVERIFY(rv.address == QString("BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L"));
    QVERIFY(rv.label == QString());

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?req-message=Wikipedia Example Address"));
    QVERIFY(GUIUtil::parseBGLURI(uri, &rv));

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?amount=1,000&label=Wikipedia Example"));
    QVERIFY(!GUIUtil::parseBGLURI(uri, &rv));

    uri.setUrl(QString("BGL:BGL1Q6SUSZC7DLTLJGGRR7S27325VQ53QE7S5CW6V7L?amount=1,000.0&label=Wikipedia Example"));
    QVERIFY(!GUIUtil::parseBGLURI(uri, &rv));
}
