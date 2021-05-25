[](share/pixmaps/BGL64.png) BGL Core integration/staging tree



[English](./README.md) | [Chinese](#) 

BGL是什么?
----------------
BGL是一种实验性的数字货币，世界上任何地方的任何人，都可以实现即时支付。
BGL使用点对点技术进行操作,没有中央权威:管理交易和发行货币由网络控制。
BGL Core是开源的名称，让你能够使用这种货币的软件。
想要了解更多信息，请阅读原 BGL白皮书。

许可证
-------
本质上，这是一个完整的比特币分叉，但是:
* Block Reward = nFees*0.1 + GetBlockSubsidy() //消耗率为tx费用的90%
* Block Weight <= 400,000;                       //比比特币小10倍
* 100% Segwit //消除遗留事务类型的问题
* Halving Interval = 210000 blocks / 4; //每年减半(比特币每4年减半)
* Block Subsidy = 50 * 4;                         // 2100万金币
* block的哈希算法是 Keccak (sha-3)。
`master`分支是定期构建的(参见doc/build-*。Md为指令)和测试，但不能保证
完全稳定。创建的[标记](https://github.com/BitgesellOfficial/bitgesell/tags)
版本，将会定期显示新的官方的、稳定的BGL核心版本。

https://github.com/BGL-core/gui 存储库是专门用于开发的GUI。它的主分支在所有的单树中是相同的存储库。
发行分支和标签不存在，所以请不要分叉除非是为了开发的原因。
官方线程:https://bitcointalk.org/index.php?topic=5238559.0

许可证
-------
测试和代码评审是开发的瓶颈;我们得到了很多的关注，导致我们需要在短时间内审查和测试的请求。
请耐心点，通过测试其他人的PR请求来帮助我们，记住这是一个注重安全的项目，任何错误都可能导致人员损失
很多钱。

# # #自动化测试
强烈鼓励开发人员为新代码编写[单元测试](src/test/README.md)，然后
为旧代码提交新的单元测试。可以编译和运行单元测试
(假设它们在configure中没有被禁用)使用: `make check`。
关于更多细节,扩展单元测试可以在[/src/test/README.md](/src/test/README.md)中找到。
还有使用Python编写的[回归和集成测试](/test)。
可以使用`test/functional/test_runner.py`运行这些测试(如果安装了[test依赖项](/test))
CI(持续集成)系统确保每个pull请求都是为Windows、Linux和macOS构建的，
并且单元/健全测试是自动运行的。

手动(QA)测试保证质量
------------
更改应该由编写程序的开发人员以外的其他人来测试代码。
这对于大的或者高风险的变更尤其重要。是很有用的.



翻译
------------
对翻译的更改和新的翻译都可以提交到
[BGL Core的Transifex页面](https://www.transifex.com/bitcoin/bitcoin/)。
翻译会定期从Transifex中提取并合并到git仓库中。看到

[translation process](doc/translation_process.md)详细介绍如何工作。
**重要的是**:我们不接受翻译更改作为GitHub pull请求，因为下一个
pull from Transifex会自动再次覆盖它们。