# Libraries

| Name                     | Description |
|--------------------------|-------------|
| *libBGL_cli*         | RPC client functionality used by *BGL-cli* executable |
| *libBGL_common*      | Home for common functionality shared by different executables and libraries. Similar to *libBGL_util*, but higher-level (see [Dependencies](#dependencies)). |
| *libBGL_consensus*   | Stable, backwards-compatible consensus functionality used by *libBGL_node* and *libBGL_wallet* and also exposed as a [shared library](../shared-libraries.md). |
| *BGLconsensus*       | Shared library build of static *libBGL_consensus* library |
| *libBGLkernel*       | Consensus engine and support library used for validation by *libBGL_node* and also exposed as a [shared library](../shared-libraries.md). |
| *libBGLqt*           | GUI functionality used by *BGL-qt* and *BGL-gui* executables |
| *libBGL_ipc*         | IPC functionality used by *BGL-node*, *BGL-wallet*, *BGL-gui* executables to communicate when [`--enable-multiprocess`](multiprocess.md) is used. |
| *libBGL_node*        | P2P and RPC server functionality used by *BGLd* and *BGL-qt* executables. |
| *libBGL_util*        | Home for common functionality shared by different executables and libraries. Similar to *libBGL_common*, but lower-level (see [Dependencies](#dependencies)). |
| *libBGL_wallet*      | Wallet functionality used by *BGLd* and *BGL-wallet* executables. |
| *libBGL_wallet_tool* | Lower-level wallet functionality used by *BGL-wallet* executable. |
| *libBGL_zmq*         | [ZeroMQ](../zmq.md) functionality used by *BGLd* and *BGL-qt* executables. |

## Conventions

- Most libraries are internal libraries and have APIs which are completely unstable! There are few or no restrictions on backwards compatibility or rules about external dependencies. Exceptions are *libBGL_consensus* and *libBGLkernel* which have external interfaces documented at [../shared-libraries.md](../shared-libraries.md).

- Generally each library should have a corresponding source directory and namespace. Source code organization is a work in progress, so it is true that some namespaces are applied inconsistently, and if you look at [`libBGL_*_SOURCES`](../../src/Makefile.am) lists you can see that many libraries pull in files from outside their source directory. But when working with libraries, it is good to follow a consistent pattern like:

  - *libBGL_node* code lives in `src/node/` in the `node::` namespace
  - *libBGL_wallet* code lives in `src/wallet/` in the `wallet::` namespace
  - *libBGL_ipc* code lives in `src/ipc/` in the `ipc::` namespace
  - *libBGL_util* code lives in `src/util/` in the `util::` namespace
  - *libBGL_consensus* code lives in `src/consensus/` in the `Consensus::` namespace

## Dependencies

- Libraries should minimize what other libraries they depend on, and only reference symbols following the arrows shown in the dependency graph below:

<table><tr><td>

```mermaid

%%{ init : { "flowchart" : { "curve" : "basis" }}}%%

graph TD;

BGL-cli[BGL-cli]-->libBGL_cli;

BGLd[BGLd]-->libBGL_node;
BGLd[BGLd]-->libBGL_wallet;

BGL-qt[BGL-qt]-->libBGL_node;
BGL-qt[BGL-qt]-->libBGLqt;
BGL-qt[BGL-qt]-->libBGL_wallet;

BGL-wallet[BGL-wallet]-->libBGL_wallet;
BGL-wallet[BGL-wallet]-->libBGL_wallet_tool;

libBGL_cli-->libBGL_util;
libBGL_cli-->libBGL_common;

libBGL_common-->libBGL_consensus;
libBGL_common-->libBGL_util;

libBGLkernel-->libBGL_consensus;
libBGLkernel-->libBGL_util;

libBGL_node-->libBGL_consensus;
libBGL_node-->libBGLkernel;
libBGL_node-->libBGL_common;
libBGL_node-->libBGL_util;

libBGLqt-->libBGL_common;
libBGLqt-->libBGL_util;

libBGL_wallet-->libBGL_common;
libBGL_wallet-->libBGL_util;

libBGL_wallet_tool-->libBGL_wallet;
libBGL_wallet_tool-->libBGL_util;

classDef bold stroke-width:2px, font-weight:bold, font-size: smaller;
class BGL-qt,BGLd,BGL-cli,BGL-wallet bold
```
</td></tr><tr><td>

**Dependency graph**. Arrows show linker symbol dependencies. *Consensus* lib depends on nothing. *Util* lib is depended on by everything. *Kernel* lib depends only on consensus and util.

</td></tr></table>

- The graph shows what _linker symbols_ (functions and variables) from each library other libraries can call and reference directly, but it is not a call graph. For example, there is no arrow connecting *libBGL_wallet* and *libBGL_node* libraries, because these libraries are intended to be modular and not depend on each other's internal implementation details. But wallet code is still able to call node code indirectly through the `interfaces::Chain` abstract class in [`interfaces/chain.h`](../../src/interfaces/chain.h) and node code calls wallet code through the `interfaces::ChainClient` and `interfaces::Chain::Notifications` abstract classes in the same file. In general, defining abstract classes in [`src/interfaces/`](../../src/interfaces/) can be a convenient way of avoiding unwanted direct dependencies or circular dependencies between libraries.

- *libBGL_consensus* should be a standalone dependency that any library can depend on, and it should not depend on any other libraries itself.

- *libBGL_util* should also be a standalone dependency that any library can depend on, and it should not depend on other internal libraries.

- *libBGL_common* should serve a similar function as *libBGL_util* and be a place for miscellaneous code used by various daemon, GUI, and CLI applications and libraries to live. It should not depend on anything other than *libBGL_util* and *libBGL_consensus*. The boundary between _util_ and _common_ is a little fuzzy but historically _util_ has been used for more generic, lower-level things like parsing hex, and _common_ has been used for BGL-specific, higher-level things like parsing base58. The difference between util and common is mostly important because *libBGLkernel* is not supposed to depend on *libBGL_common*, only *libBGL_util*. In general, if it is ever unclear whether it is better to add code to *util* or *common*, it is probably better to add it to *common* unless it is very generically useful or useful particularly to include in the kernel.


- *libBGLkernel* should only depend on *libBGL_util* and *libBGL_consensus*.

- The only thing that should depend on *libBGLkernel* internally should be *libBGL_node*. GUI and wallet libraries *libBGLqt* and *libBGL_wallet* in particular should not depend on *libBGLkernel* and the unneeded functionality it would pull in, like block validation. To the extent that GUI and wallet code need scripting and signing functionality, they should be able to get it from *libBGL_consensus*, *libBGL_common*, and *libBGL_util*, instead of *libBGLkernel*.

- GUI, node, and wallet code internal implementations should all be independent of each other, and the *libBGLqt*, *libBGL_node*, *libBGL_wallet* libraries should never reference each other's symbols. They should only call each other through [`src/interfaces/`](../../src/interfaces/) abstract interfaces.

## Work in progress

- Validation code is moving from *libBGL_node* to *libBGLkernel* as part of [The libbitcoinkernel Project #24303](https://github.com/bitcoin/bitcoin/issues/24303)
- Source code organization is discussed in general in [Library source code organization #15732](https://github.com/bitcoin/bitcoin/issues/15732)
