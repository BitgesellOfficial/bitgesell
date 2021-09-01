// Copyright (c) 2021 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <interfaces/init.h>
#include <node/context.h>

#include <memory>

namespace init {
namespace {
class BGLdInit : public interfaces::Init
{
public:
    BGLdInit(NodeContext& node) : m_node(node)
    {
        m_node.init = this;
    }
    NodeContext& m_node;
};
} // namespace
} // namespace init

namespace interfaces {
std::unique_ptr<Init> MakeNodeInit(NodeContext& node, [[maybe_unused]] int argc, [[maybe_unused]] char* argv[], [[maybe_unused]] int& exit_status)
{
    return std::make_unique<init::BGLdInit>(node);
}
} // namespace interfaces
