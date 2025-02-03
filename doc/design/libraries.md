# Libraries

| Name                     | Description |
|--------------------------|-------------|
| *libBGL_cli*         | RPC client functionality used by *BGL-cli* executable |
| *libBGL_common*      | Home for common functionality shared by different executables and libraries. Similar to *libBGL_util*, but higher-level (see [Dependencies](#dependencies)). |
| *libBGL_consensus*   | Consensus functionality used by *libBGL_node* and *libBGL_wallet*. |
| *libBGL_crypto*      | Hardware-optimized functions for data encryption, hashing, message authentication, and key derivation. |
| *libBGL_kernel*      | Consensus engine and support library used for validation by *libBGL_node*. |
| *libBGLqt*           | GUI functionality used by *BGL-qt* and *BGL-gui* executables. |
| *libBGL_ipc*         | IPC functionality used by *BGL-node*, *BGL-wallet*, *BGL-gui* executables to communicate when [`-DENABLE_IPC=ON`](multiprocess.md) is used. |
| *libBGL_node*        | P2P and RPC server functionality used by *BGLd* and *BGL-qt* executables. |
| *libBGL_util*        | Home for common functionality shared by different executables and libraries. Similar to *libBGL_common*, but lower-level (see [Dependencies](#dependencies)). |
| *libBGL_wallet*      | Wallet functionality used by *BGLd* and *BGL-wallet* executables. |
| *libBGL_wallet_tool* | Lower-level wallet functionality used by *BGL-wallet* executable. |
| *libBGL_zmq*         | [ZeroMQ](../zmq.md) functionality used by *BGLd* and *BGL-qt* executables. |

## Conventions

- Most libraries are internal libraries and have APIs which are completely unstable! There are few or no restrictions on backwards compatibility or rules about external dependencies. Exceptions are *libBGL_consensus* and *libBGL_kernel* which have external interfaces documented at [../shared-libraries.md](../shared-libraries.md).

- Generally each library should have a corresponding source directory and namespace. Source code organization is a work in progress, so it is true that some namespaces are applied inconsistently, and if you look at [`add_library(BGL_* ...)`](../../src/CMakeLists.txt) lists you can see that many libraries pull in files from outside their source directory. But when working with libraries, it is good to follow a consistent pattern like:

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

libBGL_kernel-->libBGL_consensus;
libBGL_kernel-->libBGL_util;

libBGL_node-->libBGL_consensus;
libBGL_node-->libBGL_kernel;
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

- *libBGL_util* should be a standalone dependency that any library can depend on, and it should not depend on other libraries except *libBGL_crypto*. It provides basic utilities that fill in gaps in the C++ standard library and provide lightweight abstractions over platform-specific features. Since the util library is distributed with the kernel and is usable by kernel applications, it shouldn't contain functions that external code shouldn't call, like higher level code targeted at the node or wallet. (*libBGL_common* is a better place for higher level code, or code that is meant to be used by internal applications only.)


- *libBGL_kernel* should only depend on *libBGL_util* and *libBGL_consensus*.

- The only thing that should depend on *libBGL_kernel* internally should be *libBGL_node*. GUI and wallet libraries *libBGLqt* and *libBGL_wallet* in particular should not depend on *libBGL_kernel* and the unneeded functionality it would pull in, like block validation. To the extent that GUI and wallet code need scripting and signing functionality, they should be able to get it from *libBGL_consensus*, *libBGL_common*, *libBGL_crypto*, and *libBGL_util*, instead of *libBGL_kernel*.

- GUI, node, and wallet code internal implementations should all be independent of each other, and the *libBGLqt*, *libBGL_node*, *libBGL_wallet* libraries should never reference each other's symbols. They should only call each other through [`src/interfaces/`](../../src/interfaces/) abstract interfaces.

## Work in progress

- Validation code is moving from *libBGL_node* to *libBGL_kernel* as part of [The libBGLkernel Project #27587](https://github.com/bitcoin/bitcoin/issues/27587)
