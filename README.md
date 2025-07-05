# PDF to PNG Converter

## 概要

このアプリケーションは、PDFファイルをアップロードし、各ページをPNG画像に変換して表示するシンプルなWebツールです。PythonのFlaskフレームワークとPyMuPDFライブラリを使用しており、メモリ上で効率的に変換処理を行います。

## 機能

-   PDFファイルのアップロードとPNG画像への変換
-   変換されたPNG画像をBase64エンコードされたデータURLとして表示
-   インメモリでのPDF処理（ディスクへの一時保存なし）
-   アップロードファイルサイズの制限（デフォルト30MB）
-   Nginxなどのリバースプロキシによるサブディレクトリデプロイ対応（例: `/pdf2png`）
-   DPI設定（デフォルト300DPI）

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

### 直接実行

`app.py`に実行権限を付与している場合、以下のコマンドで直接アプリケーションを起動できます。

```bash
./app.py
```

### Pythonインタープリタを使用して実行

```bash
python3 app.py
```

アプリケーションはデフォルトで `http://0.0.0.0:5000` (または `http://[::]:5000` for IPv6) で起動します。

## Nginxとの連携 (オプション)

このアプリケーションは、Nginxなどのリバースプロキシのサブディレクトリ（例: `/pdf2png`）で動作するように設計されています。`app.py`内の`PrefixMiddleware`がこの設定を処理します。

Nginxの設定例（一部抜粋）：

```nginx
location /pdf2png/ {
    proxy_pass http://127.0.0.1:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    client_max_body_size 35M; # アプリケーションのMAX_CONTENT_LENGTHより大きい値を設定
}
```

**注意:** Nginxの`client_max_body_size`は、アプリケーションの`MAX_CONTENT_LENGTH`（デフォルト30MB）よりも大きな値を設定してください。そうしないと、Nginxが先に大きなファイルのアップロードを拒否してしまいます。

## 注意点

-   **最大ファイルサイズ**: 現在、アップロードできるPDFファイルの最大サイズは30MBに設定されています。これは、1GBのRAMを搭載したWebサーバーでの動作を想定した目安です。PDFのページ数や内容によっては、このサイズでもメモリ不足になる可能性があります。
-   **メモリ使用量**: 変換されたすべてのPNG画像データはメモリ上に保持されるため、ページ数の多いPDFや高解像度のPDFを変換すると、大量のメモリを消費する可能性があります。サーバーのRAM容量に応じて、アップロードファイルサイズやDPI設定を調整してください。
