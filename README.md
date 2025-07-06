# PDF to PNG Converter

## 概要

このプロジェクトは、PDFファイルをPNG画像に変換するためのツールを提供します。主に以下の2つのコンポーネントで構成されています。

1.  **Webアプリケーション**: PDFファイルをアップロードし、各ページをPNG画像に変換してブラウザに表示するシンプルなWebツールです。PythonのFlaskフレームワークとPyMuPDFライブラリを使用しており、メモリ上で効率的に変換処理を行います。
2.  **CLIツール**: 指定されたディレクトリ内のPDFファイルを一括でPNG画像に変換するコマンドラインツールです。

## 機能

### Webアプリケーション

-   PDFファイルのアップロードとPNG画像への変換
-   変換されたPNG画像をBase64エンコードされたデータURLとして表示
-   インメモリでのPDF処理（ディスクへの一時保存なし）
-   アップロードファイルサイズの制限（デフォルト30MB）
-   Nginxなどのリバースプロキシによるサブディレクトリデプロイ対応（例: `/pdf2png`）
-   DPI設定（デフォルト300DPI）

### CLIツール (`pdf_to_png.py`)

-   指定ディレクトリ内のすべてのPDFファイルをPNG画像に一括変換
-   ページごとに個別のPNGファイルを生成
-   出力ディレクトリの自動作成

## セットアップ

### 必要なもの

-   Python 3.x
-   pip (Pythonのパッケージインストーラ)

### 依存ライブラリのインストール

以下のコマンドを実行して、必要なPythonライブラリをインストールします。

```bash
pip install Flask PyMuPDF
```

Ubuntuの場合、以下のコマンドでインストールすることも可能です。

```bash
sudo apt install -y python3-flask python3-fitz
```

## 実行方法

### Webアプリケーション

`app.py`に実行権限を付与している場合、以下のコマンドで直接アプリケーションを起動できます。

```bash
./app.py
```

または、Pythonインタープリタを使用して実行します。

```bash
python3 app.py
```

アプリケーションはデフォルトで `http://0.0.0.0:5000` (または `http://[::]:5000` for IPv6) で起動します。

### CLIツール

`pdf_to_png.py` を使用して、指定したディレクトリ内のPDFファイルをPNGに変換できます。

1.  変換したいPDFファイルを `pdf` という名前のディレクトリに配置します。
2.  以下のコマンドを実行します。

    ```bash
    python3 pdf_to_png.py
    ```

    変換されたPNG画像は `img` ディレクトリに保存されます。

### Systemdサービスとしての運用

`ctl.sh` スクリプトを使用して、WebアプリケーションをSystemdサービスとして管理できます。

1.  **初期設定**: サービスファイルをSystemdに登録し、有効化します。
    ```bash
    sudo /home/shino/development/pdf-to-png/ctl.sh init
    ```
    このコマンドは、`/home/shino/development/pdf-to-png/pdf-to-png.service` を `/etc/systemd/system/pdf2png.service` にシンボリックリンクし、`systemctl daemon-reload` と `systemctl enable pdf2png.service` を実行します。

2.  **サービスの開始/停止/再起動/ステータス確認**:
    ```bash
    sudo /home/shino/development/pdf-to-png/ctl.sh start
    sudo /home/shino/development/pdf-to-png/ctl.sh stop
    sudo /home/shino/development/pdf-to-png/ctl.sh restart
    sudo /home/shino/development/pdf-to-png/ctl.sh status
    ```

## Nginxとの連携 (オプション)

このアプリケーションは、Nginxなどのリバースプロキシのサブディレクトリ（例: `/pdf2png`）で動作するように設計されています。`app.py`内の`PrefixMiddleware`がこの設定を処理します。

Nginxの設定例（一部抜粋）：

```nginx
location /pdf2png/ {
    proxy_pass http://127.0.0.1:5000/pdf2png/; # ここを修正
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    client_max_body_size 35M; # アプリケーションのMAX_CONTENT_LENGTHより大きい値を設定
}
```

**注意:** Nginxの`client_max_body_size`は、アプリケーションの`MAX_CONTENT_LENGTH`（デフォルト30MB）よりも大きな値を設定してください。そうしないと、Nginxが先に大きなファイルのアップロードを拒否してしまいます。

## 開発・運用スクリプト

プロジェクトには、開発と運用を補助するためのシェルスクリプトが含まれています。

-   `ctl.sh`: Systemdサービス (`pdf2png.service`) の管理に使用します。`init`, `start`, `stop`, `restart`, `status` コマンドをサポートします。
-   `pull.sh`: Gitリポジトリから最新の変更をプルし、Webアプリケーションサービスを再起動します。
-   `push.sh`: `app.py` の変更をコミットし、Gitリポジリにプッシュします。

## 注意点

-   **最大ファイルサイズ**: 現在、アップロードできるPDFファイルの最大サイズは30MBに設定されています。これは、1GBのRAMを搭載したWebサーバーでの動作を想定した目安です。PDFのページ数や内容によっては、このサイズでもメモリ不足になる可能性があります。
-   **メモリ使用量**: 変換されたすべてのPNG画像データはメモリ上に保持されるため、ページ数の多いPDFや高解像度のPDFを変換すると、大量のメモリを消費する可能性があります。サーバーのRAM容量に応じて、アップロードファイルサイズやDPI設定を調整してください。