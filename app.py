import io
import base64
import fitz  # PyMuPDF
from flask import Flask, request, render_template, redirect, url_for

class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path.startswith(self.prefix):
            environ['PATH_INFO'] = path[len(self.prefix):]
            # Ensure the path info starts with a / for routing
            if not environ['PATH_INFO'].startswith('/'):
                environ['PATH_INFO'] = '/' + environ['PATH_INFO']
            environ['SCRIPT_NAME'] = self.prefix
        return self.app(environ, start_response)

app = Flask(__name__)

# Nginxのサブルート設定に合わせてプレフィックスを適用
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/pdf2png')


# メモリ使用量の上限を設定（例: 16MB）
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 許可する拡張子
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_pdf_to_base64_images(pdf_bytes):
    """メモリ上のPDFデータをBase64エンコードされたPNG画像のリストに変換する"""
    base64_images = []
    try:
        # メモリ上のバイトデータからPDFを開く
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_num in range(len(doc)):
            page = doc[page_num]  # ページをインデックスで取得
            pix = page.get_pixmap(dpi=200) # DPIを少し下げてメモリ使用量を調整
            
            # PNGデータをメモリ上のバイトバッファに書き出す
            img_bytes = pix.tobytes("png")
            
            # Base64にエンコードして、HTMLで使える形式にする
            base64_encoded = base64.b64encode(img_bytes).decode('utf-8')
            data_url = f"data:image/png;base64,{base64_encoded}"
            base64_images.append(data_url)
        
        doc.close()
    except Exception as e:
        error_message = f"PDF変換中にエラーが発生しました: {e}"
        print(error_message)
        return None, error_message
    return base64_images, None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # ファイルを保存せず、メモリ上のバイトデータとして読み込む
            pdf_bytes = file.read()
            
            # メモリ上で変換処理を実行
            images_data, error = convert_pdf_to_base64_images(pdf_bytes)

            if images_data is not None:
                # 結果を直接テンプレートに渡してレンダリング
                return render_template('results.html', images=images_data)
            else:
                # エラーメッセージをユーザーに表示
                user_error_message = f"変換に失敗しました。PDFファイルが破損しているか、サポートされていない形式の可能性があります。<br><br>詳細情報: {error}"
                return user_error_message, 400

    return render_template('index.html')

if __name__ == '__main__':
    # IPv6とIPv4の両方で待機
    app.run(host='::', port=5000, debug=True)