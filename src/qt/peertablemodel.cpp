// Copyright (c) 2011-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <qt/peertablemodel.h>

#include <qt/guiconstants.h>
#include <qt/guiutil.h>

#include <interfaces/node.h>

#include <utility>

#include <QDebug>
#include <QList>
#include <QTimer>

PeerTableModel::PeerTableModel(interfaces::Node& node, QObject* parent) :
    QAbstractTableModel(parent),
    m_node(node),
    timer(nullptr)
{
    // set up timer for auto refresh
    timer = new QTimer(this);
    connect(timer, &QTimer::timeout, this, &PeerTableModel::refresh);
    timer->setInterval(MODEL_UPDATE_DELAY);

    // load initial data
    refresh();
}

PeerTableModel::~PeerTableModel()
{
    // Intentionally left empty
}

void PeerTableModel::startAutoRefresh()
{
    timer->start();
}

void PeerTableModel::stopAutoRefresh()
{
    timer->stop();
}

int PeerTableModel::rowCount(const QModelIndex& parent) const
{
    if (parent.isValid()) {
        return 0;
    }
    return m_peers_data.size();
}

int PeerTableModel::columnCount(const QModelIndex& parent) const
{
    if (parent.isValid()) {
        return 0;
    }
    return columns.length();
}

QVariant PeerTableModel::data(const QModelIndex& index, int role) const
{
    if(!index.isValid())
        return QVariant();

    CNodeCombinedStats *rec = static_cast<CNodeCombinedStats*>(index.internalPointer());

    const auto column = static_cast<ColumnIndex>(index.column());
    if (role == Qt::DisplayRole) {
        switch (column) {
        case NetNodeId:
            return (qint64)rec->nodeStats.nodeid;
        case Address:
            return QString::fromStdString(rec->nodeStats.addrName);
        case Direction:
            return QString(rec->nodeStats.fInbound ?
                               //: An Inbound Connection from a Peer.
                               tr("Inbound") :
                               //: An Outbound Connection to a Peer.
                               tr("Outbound"));
        case ConnectionType:
            return GUIUtil::ConnectionTypeToQString(rec->nodeStats.m_conn_type, /* prepend_direction */ false);
        case Network:
            return GUIUtil::NetworkToQString(rec->nodeStats.m_network);
        case Ping:
            return GUIUtil::formatPingTime(rec->nodeStats.m_min_ping_time);
        case Sent:
            return GUIUtil::formatBytes(rec->nodeStats.nSendBytes);
        case Received:
            return GUIUtil::formatBytes(rec->nodeStats.nRecvBytes);
        case Subversion:
            return QString::fromStdString(rec->nodeStats.cleanSubVer);
        } // no default case, so the compiler can warn about missing cases
        assert(false);
    } else if (role == Qt::TextAlignmentRole) {
        switch (column) {
        case NetNodeId:
            return QVariant(Qt::AlignRight | Qt::AlignVCenter);
        case Address:
            return {};
        case Direction:
        case ConnectionType:
        case Network:
            return QVariant(Qt::AlignCenter);
        case Ping:
        case Sent:
        case Received:
            return QVariant(Qt::AlignRight | Qt::AlignVCenter);
        case Subversion:
            return {};
        } // no default case, so the compiler can warn about missing cases
        assert(false);
    } else if (role == StatsRole) {
        switch (index.column()) {
        case NetNodeId: return QVariant::fromValue(rec);
        default: return QVariant();
        }
    }

    return QVariant();
}

QVariant PeerTableModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    if(orientation == Qt::Horizontal)
    {
        if(role == Qt::DisplayRole && section < columns.size())
        {
            return columns[section];
        }
    }
    return QVariant();
}

Qt::ItemFlags PeerTableModel::flags(const QModelIndex &index) const
{
    if (!index.isValid()) return Qt::NoItemFlags;

    Qt::ItemFlags retval = Qt::ItemIsSelectable | Qt::ItemIsEnabled;
    return retval;
}

QModelIndex PeerTableModel::index(int row, int column, const QModelIndex& parent) const
{
    Q_UNUSED(parent);

    if (0 <= row && row < rowCount() && 0 <= column && column < columnCount()) {
        return createIndex(row, column, const_cast<CNodeCombinedStats*>(&m_peers_data[row]));
    }

    return QModelIndex();
}

void PeerTableModel::refresh()
{
    interfaces::Node::NodesStats nodes_stats;
    m_node.getNodesStats(nodes_stats);
    decltype(m_peers_data) new_peers_data;
    new_peers_data.reserve(nodes_stats.size());
    for (const auto& node_stats : nodes_stats) {
        const CNodeCombinedStats stats{std::get<0>(node_stats), std::get<2>(node_stats), std::get<1>(node_stats)};
        new_peers_data.append(stats);
    }

    Q_EMIT layoutAboutToBeChanged();
    m_peers_data.swap(new_peers_data);
    Q_EMIT layoutChanged();
}

int PeerTableModel::getRowByNodeId(NodeId nodeid)
{
    std::map<NodeId, int>::iterator it = priv->mapNodeRows.find(nodeid);
    if (it == priv->mapNodeRows.end())
        return -1;

    return it->second;
}

void PeerTableModel::sort(int column, Qt::SortOrder order)
{
    priv->sortColumn = column;
    priv->sortOrder = order;
    refresh();
}
