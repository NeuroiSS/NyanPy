# NyanPy

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/01.png)

NyanPyはPySide6（Python版Qtライブラリ）をベースに開発されたGUIアプリケーション群です。私がほしいと思った機能を追加します。

## 1. 動作環境

- Python 3.12+

- NumPy

- PySide6

- PyQtGraph

Windows 11のパソコンで開発をしています。OS違いだと見た目が崩れたりすると思います。許してください。

## 2. インストール

***STEP 1.***

まずは、Pythonをインストールする必要があります。既にインストール済みの場合はスキップしてください。Windowsの方には「Chocolatey」を使ったインストールがおすすめです。ChocolateyはWindows用のパッケージ管理ツールで、Linuxの「apt」やMacの「homebrew」と同様に使うことができます。Chocolateyの導入方法は他を参照してください。

Windowsの場合：

```shell-session
$ choco install python
$ choco install pip
```

***STEP 2.***

Pythonの依存ライブラリ（NumPy、PySide6、PyQtGraph）をインストールします。既にインストール済みの場合はスキップしてください。

```shell-session
$ pip install numpy pyside6 pyqtgraph
```

***STEP 3.***

このNyanPyプロジェクト一式をダウンロードしてください。

Gitを使う方法：

```shell-session
$ git clone https://github.com/NeuroiSS/NyanPy.git
```

Gitを使わない方法：

Githubのページ右上の「Code」ボタンをクリックすると「Download ZIP」できます。ダウンロードしたら、ZIPファイルを解凍してください。置く場所はどこでも大丈夫です（たぶん）。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/02.png)

***STEP 4.***

以下の方法でアプリを起動します。

コマンド（CUI）で起動する方法：

NyanPyディレクトリに移動して下のコマンドを実行します。

```shell-session
$ python -m NyanPy
```

バッチファイルで起動する方法（Windows）：

Windowsの場合、NyanPyフォルダ内のバッチファイル「run.bat」をダブルクリックすると起動できます。

## 3. 機能紹介、こだわりポイント

各アプリを紹介します。すべてランチャーから起動することができます。ランチャーは猫アイコンで、ランチャーから起動したアプリは肉球アイコンになります（ここ、一番のこだわりポイントです）。

### 3.1. AnalogClock - シンプルなアナログ時計

アナログ時計を表示できます。Windows 7のガジェットのような感じにできます。右クリックから「Window Stays on Top」を選択すると、ウィンドウを常に一番上に置いておけます。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/03.png)

### 3.2. CodeEditor - PythonとMATLAB/GNU Octave用コードエディタ

テキストエディタです。PythonとMATLAB/GNU Octaveのシンタクスハイライトを実装しました。タブはハードタブとソフトタブを切り替えられます。見た目は愛用しているVimのJellybeansテーマを真似ました。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/04.png)

...

作ってみたけど、普段はNeovimを使用しているのであまり使い道がなかった...。Neovim最高！！！

### 3.3. SheetEditor - Vimmerのためのスプレッドシート

Vimライクなスプレッドシートです。私はエクセルを使うのがとても苦手なので、Vimみたいなスプレッドシートがあったらいいなあと思い作りました。かなり自信作です。

**・カーソル移動**

Vimのように、"hjkl"キーでカーソル移動できます。

**・モード切替**

Vimのように、5つのモード（NORMAL、INSERT、INSERT-LINE、VISUAL、VISUAL-LINE）が存在し、それぞれ異なる編集機能が割り当てられています。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/05.gif)

"i"キーを押すとINSERTモードに遷移します。INSERTモードでは、方向キー"hjkl"により選択箇所に行と列を挿入・除去することができます。VimのINSERTモードとはちょっと違いますね。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/06.gif)

"Shift+i"キーを押すとINSERT-LINEモードに遷移します。INSERT-LINEモードでは、方向キー"hjkl"により行全体、列全体を追加・除去することができます。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/07.gif)

"v"キーを押すとVISUALモードに遷移します。VISUALモードでは、方向キー"hjkl"により矩形選択することができます。VimのV-BLOCKモードと似ています。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/08.gif)

"Shift+v"を押すとVISUAL-LINEモードに遷移します。VISUAL-LINEモードでは、方向キー"hjkl"により行全体または列全体を選択することができます。VimのV-LINEモードに似ています。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/09.gif)

**・ショートカットキー**

"Ctrl+C":Copy、"Ctrl+V":Paste、"Ctrl+Z":Undo等の一般的なショートカットキーに加えて、Vimライクなショートカットキー、たとえば、"y":Yank、"p":Put、"u":Undo等も割り当てています。

**・コマンド**

Vimのように、コロンを打つとコマンド入力状態になります（Vimと違い、モード遷移はしません）。":e"でファイルを開く、":w"で保存、":s"で検索など、Vimっぽいコマンドを使うことができます。

**・変数（Variables）**

データに名前を付けて、変数として扱えるようにしました。変数定義にPythonの式やNumPyの関数等を使用することができるので、複雑な計算処理も可能です。

下の例では、reS11とimS11というベクトルデータを変数に格納し、「reS11+1j*imS11」という複素数に変換して、結果を表に出力しています。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/10.gif)

**・グラフ作成**

PyQtGraphをベースとしたグラフプロットツールを作りました。タイトル、軸ラベル、範囲、グリッド、線の色、太さ、点の大きさ、形、凡例、余白、などなど、細かい調整が可能です。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/11.png)

### 3.4. TouchstoneViewer - Sパラメータファイル（SnP）のビューア

タッチストーンファイル（Sパラメータ）のビューアです。SパラメータをZ、Y、H、ABCDパラメータや群遅延、Kファクタ、GMAX等に変換してプロットすることもできます。Mag/Phase/Re/Im/Smith/Admittance Smith/Polar等、プロットの種類を選べます。Sパラメータをよく扱う私にとっては超便利ツールです。

![img](https://raw.githubusercontent.com/NeuroiSS/NyanPy/master/docs/README/12.png)
