// Copyright (c) 2014-2021 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_QT_WINSHUTDOWNMONITOR_H
#define BGL_QT_WINSHUTDOWNMONITOR_H

#ifdef WIN32
#include <QByteArray>
#include <QString>
#include <functional>

#include <windows.h>

#include <QAbstractNativeEventFilter>

class WinShutdownMonitor : public QAbstractNativeEventFilter
{
public:
    WinShutdownMonitor(std::function<void()> shutdown_fn) : m_shutdown_fn{std::move(shutdown_fn)} {}

    /** Implements QAbstractNativeEventFilter interface for processing Windows messages */
    bool nativeEventFilter(const QByteArray &eventType, void *pMessage, long *pnResult);

    /** Register the reason for blocking shutdown on Windows to allow clean client exit */
    static void registerShutdownBlockReason(const QString& strReason, const HWND& mainWinId);

private:
    std::function<void()> m_shutdown_fn;
};
#endif

#endif // BGL_QT_WINSHUTDOWNMONITOR_H
