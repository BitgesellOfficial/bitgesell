// Copyright (c) 2023 Bitcoin Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include "logprintf.h"

#include <clang-tidy/ClangTidyModule.h>
#include <clang-tidy/ClangTidyModuleRegistry.h>

class BGLModule final : public clang::tidy::ClangTidyModule
{
public:
    void addCheckFactories(clang::tidy::ClangTidyCheckFactories& CheckFactories) override
    {
        CheckFactories.registerCheck<BGL::LogPrintfCheck>("BGL-unterminated-logprintf");
    }
};

static clang::tidy::ClangTidyModuleRegistry::Add<BGLModule>
    X("BGL-module", "Adds BGL checks.");

volatile int BGLModuleAnchorSource = 0;
