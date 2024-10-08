// Copyright (c) 2018-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_BGL_CONFIG_H
#define BGL_BGL_CONFIG_H

/* Version Build */
#define CLIENT_VERSION_BUILD 13

/* Version is release */
#define CLIENT_VERSION_IS_RELEASE true

/* Major version */
#define CLIENT_VERSION_MAJOR 0

/* Minor version */
#define CLIENT_VERSION_MINOR 1

/* Copyright holder(s) before %s replacement */
#define COPYRIGHT_HOLDERS "The %s developers"

/* Copyright holder(s) */
#define COPYRIGHT_HOLDERS_FINAL "The Bitgesell Core developers"

/* Replacement for %s in copyright holders string */
#define COPYRIGHT_HOLDERS_SUBSTITUTION "Bitgesell Core"

/* Copyright year */
#define COPYRIGHT_YEAR 2024

/* Define to 1 to enable wallet functions */
#define ENABLE_WALLET 1

/* Define to 1 to enable BDB wallet */
#define USE_BDB 1

/* Define to 1 to enable SQLite wallet */
#define USE_SQLITE 1

/* Define this symbol to enable ZMQ functions */
#define ENABLE_ZMQ 1

/* Define to 1 if you have the declaration of `fork', and to 0 if you don't.
   */
#define HAVE_DECL_FORK 0

/* Define to 1 if you have the declaration of `setsid', and to 0 if you don't.
   */
#define HAVE_DECL_SETSID 0

/* Define if the dllexport attribute is supported. */
#define HAVE_DLLEXPORT_ATTRIBUTE 1

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT "https://github.com/bitgesellofficial/bitgesell/issues"

/* Define to the full name of this package. */
#define PACKAGE_NAME "Bitgesell Core"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "BGL Core 0.1.13"

/* Define to the home page for this package. */
#define PACKAGE_URL "https://github.com/BitgesellOfficial/bitgesell/releases/"

/* Define to the version of this package. */
#define PACKAGE_VERSION "0.1.13"

/* Define this symbol if the minimal qt platform exists */
#define QT_QPA_PLATFORM_MINIMAL 1

/* Define this symbol if the qt platform is windows */
#define QT_QPA_PLATFORM_WINDOWS 1

/* Define this symbol if qt plugins are static */
#define QT_STATICPLUGIN 1

/* Windows Universal Platform constraints */
#if !defined(WINAPI_FAMILY) || (WINAPI_FAMILY == WINAPI_FAMILY_DESKTOP_APP)
/* Either a desktop application without API restrictions, or and older system
   before these macros were defined. */

/* ::wsystem is available */
#define HAVE_SYSTEM 1

#endif // !WINAPI_FAMILY || WINAPI_FAMILY_DESKTOP_APP

#endif //BGL_BGL_CONFIG_H
