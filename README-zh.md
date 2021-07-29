<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/BitgesellOfficial/bitgesell">
    <img src="https://github.com/BitgesellOfficial/bitgesell/blob/master/share/pixmaps/BGL64.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Bitgesell (BGL)</h3>

  <p align="center">
    Bitgesell (BGL) 是一種實驗性數字貨幣
    <br />
    <a href="https://bitgesell.ca/"><strong>探索更多關於項目 »</strong></a>
    <br />
    <br />
    <a href="#">English</a>
    ·
    <a href="https://github.com/BitgesellOfficial/bitgesell/blob/master/README-zh.md">Chinese</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>目錄</summary>
  <ol>
    <li>
      <a href="#about-the-project">關於該項目</a>
      <ul>
        <li><a href="#built-with">內置</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">入門</a>
      <!-- <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul> -->
    </li>
    <li><a href="#roadmap">路線圖</a></li>
    <li><a href="#contributing">貢獻</a></li>
    <li><a href="#license">執照</a></li>
    <li><a href="#contact">接觸</a></li>
    <li><a href="#acknowledgements">翻譯</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## 關於該項目

![Product Name Screen Shot](https://github.com/BitgesellOfficial/bitgesell/blob/master/share/pixmaps/BGL64.png) 

BGL 是一種實驗性數字貨幣，可以向世界上任何地方的任何人即時付款。BGL 使用點對點技術在沒有中央權限的情況下運行：管理交易和發行貨幣由網絡共同執行。 BGL Core 是允許使用這種貨幣的開源軟件的名稱。

<b>Bitgesell 是比特幣的一個分支，有以下變化：</b> <br>
* 區塊獎勵 [燃燒率是交易費用的 90%]
  ```sh
  nFees*0.1 + GetBlockSubsidy()  
  ```
* 區塊重量 [比比特幣小 10 倍]
  ```sh
  <= 400,000
  ```
* 100% Segwit 
  ```sh
  消除遺留類型交易的問題
  ```
* 減半間隔 [bitgetsell 的減半週期為 1 年，而比特幣的減半週期為 4 年]
  ```sh
  210000 blocks/4
  ```
* 區塊補貼 [最大硬幣 = 21,000,000] <br>
  `210000 blocks/4` <br> <hr>
  `塊的哈希算法是 Keccak (sha-3).` <br> <hr>
  `master 分支定期搭建 (看` [doc/build-*.md](https://github.com/BitgesellOfficial/bitgesell/tree/master/doc) `說明) 並經過測試，但不保證完全穩定。` <br> <hr>
  [標籤](https://github.com/BitgesellOfficial/bitgesell/tags) `定期創建，以指示 BGL Core 的新官方穩定發行版本。` <br>
 
 
### 內置

* [C++](#)
* [C](#)
* [Python](#)
* [SourcePawn](#)
* [M4](#)
* [Shell](#)


<!-- GETTING STARTED -->
## 入門

[GUI](https://github.com/BGL-core/gui) 存儲庫專門用於 GUI 的開發。它的 master 分支在所有 monotree 存儲庫中都是相同的。發布分支和標籤不存在，所以除非出於開發原因，否則請不要分叉該存儲庫。

官方線程: [點擊這裡](https://bitcointalk.org/index.php?topic=5238559.0)


### 自動化測試

強烈鼓勵開發人員為新代碼編寫 [單元測試](https://github.com/BitgesellOfficial/bitgesell/blob/master/src/test/README.md)，並
為舊代碼提交新的單元測試。可以編譯和運行單元測試
（假設它們在配置中沒有被禁用）：`make check`。關於跑步的更多細節
擴展單元測試可以在 [src/test/README.md](https://github.com/BitgesellOfficial/bitgesell/blob/master/src/test/README.md) 中找到。 <br>

還有 [回歸和集成測試](https://github.com/BitgesellOfficial/bitgesell/tree/master/test)，寫的
在 Python 中。 <br>
這些測試可以運行 [如果[測試依賴項](https://github.com/BitgesellOfficial/bitgesell/tree/master/test) 與: `test/functional/test_runner.py` <br>

CI（持續集成）系統確保每個拉取請求都是為 Windows、Linux 和 macOS 構建的，
並且自動運行單元/健全性測試. <br>


### 手動質量保證 (QA) 測試

更改應由編寫該更改的開發人員以外的其他人進行測試
代碼。這對於大的或高風險的變化尤其重要。它是有益的
如果測試更改，則將測試計劃添加到拉取請求描述中
不直截了當。


<!-- ROADMAP -->
## 路線圖

請參閱 [open issues](https://github.com/BitgesellOfficial/bitgesell/issues) 以獲取建議功能（和已知問題）的列表。


<!-- CONTRIBUTING -->
## 貢獻

貢獻使開源社區成為學習、啟發和創造的絕佳場所。 **非常感謝您做出的任何貢獻**。

1. 分叉項目
2. 創建你的功能分支
3. 提交您的更改
4.推送到分行
5.打開拉取請求



<!-- LICENSE -->
## 執照

在 MIT 許可下分發。有關更多信息，請參閱 [許可證](https://github.com/BitgesellOfficial/bitgesell/blob/master/COPYING)。



<!-- CONTACT -->
## 接觸

Discord - [Bitgesell](https://discord.com/invite/Ubp359vZEF)

Twitter: [Bitgesell](https://twitter.com/Bitgesell)

Medium: [Bitgesell](https://bitgesell.medium.com/)

Facebook: [Bitgesell](https://www.facebook.com/Bitgesell)


<!-- ACKNOWLEDGEMENTS -->
## 翻譯

可以提交對翻譯的更改以及新的翻譯
[BGL Core 的 Transifex 頁面](https://www.transifex.com/bitcoin/bitcoin/)。

翻譯會定期從 Transifex 中提取並合併到 git 存儲庫中。見
[翻譯過程](doc/translation_process.md) 了解有關其工作原理的詳細信息。

**重要**：我們不接受作為 GitHub 拉取請求的翻譯更改，因為下一個
從 Transifex 拉取會自動再次覆蓋它們。

