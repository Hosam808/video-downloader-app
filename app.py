from flask import Flask, request, render_template_string, send_file, jsonify
import os
import yt_dlp
import tempfile
import shutil
import threading
import time

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>محمل الفيديوهات | Hosam Elsayed</title>
    <style>
        :root {
            --gold: #D4AF37;
            --gold-light: #F4D03F;
            --gold-dark: #B8960C;
            --black: #0A0A0A;
            --black-light: #1A1A1A;
            --black-lighter: #2A2A2A;
            --text: #E0E0E0;
            --text-muted: #A0A0A0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--black);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(212, 175, 55, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 50%, rgba(212, 175, 55, 0.03) 0%, transparent 50%);
        }
        
        .container {
            background: var(--black-light);
            border-radius: 24px;
            padding: 30px 25px;
            box-shadow: 
                0 20px 60px rgba(0,0,0,0.5),
                0 0 0 1px rgba(212, 175, 55, 0.1),
                0 0 40px rgba(212, 175, 55, 0.05);
            max-width: 500px;
            width: 100%;
            border: 1px solid rgba(212, 175, 55, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--gold), transparent);
        }
        
        .logo-icon {
            text-align: center;
            font-size: 45px;
            margin-bottom: 5px;
            filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.3));
        }
        
        h1 {
            text-align: center;
            color: var(--gold);
            margin-bottom: 5px;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        
        .subtitle {
            text-align: center;
            color: var(--text-muted);
            margin-bottom: 20px;
            font-size: 13px;
        }
        
        .input-group {
            margin-bottom: 15px;
            position: relative;
        }
        
        .input-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            color: var(--gold);
            z-index: 1;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 16px 45px 16px 16px;
            background: var(--black-lighter);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 14px;
            font-size: 15px;
            color: var(--text);
            transition: all 0.3s;
            direction: ltr;
            text-align: left;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: var(--gold);
            box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
            background: var(--black);
        }
        
        input[type="text"]::placeholder {
            color: #555;
            font-size: 13px;
        }
        
        button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold) 50%, var(--gold-light) 100%);
            color: var(--black);
            border: none;
            border-radius: 14px;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            letter-spacing: 1px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .message {
            margin-top: 15px;
            padding: 14px;
            border-radius: 14px;
            text-align: center;
            display: none;
            font-size: 13px;
            word-break: break-all;
        }
        
        .success {
            background: rgba(212, 175, 55, 0.1);
            color: var(--gold);
            display: block;
            border: 1px solid rgba(212, 175, 55, 0.3);
        }
        
        .error {
            background: rgba(255, 68, 68, 0.1);
            color: #FF4444;
            display: block;
            border: 1px solid rgba(255, 68, 68, 0.3);
        }
        
        .loading {
            background: rgba(212, 175, 55, 0.05);
            color: var(--gold-light);
            display: block;
            border: 1px solid rgba(212, 175, 55, 0.2);
        }
        
        .download-btn {
            display: inline-block;
            background: var(--gold);
            color: var(--black);
            padding: 14px 35px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 700;
            margin-top: 10px;
            transition: all 0.3s;
        }
        
        .download-btn:hover {
            background: var(--gold-light);
            box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            padding-top: 18px;
            border-top: 1px solid rgba(212, 175, 55, 0.1);
        }
        
        .footer-text {
            color: var(--text-muted);
            font-size: 11px;
            letter-spacing: 1px;
        }
        
        .footer-name {
            color: var(--gold);
            font-weight: bold;
            font-size: 13px;
        }
        
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid var(--black);
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-left: 8px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-icon">🎥</div>
        <h1>محمل الفيديوهات</h1>
        <p class="subtitle">حمل من أي منصة بأعلى جودة تلقائياً</p>
        
        <div class="input-group">
            <span class="input-icon">🔗</span>
            <input type="text" id="url" placeholder="الصق رابط الفيديو هنا..." />
        </div>
        
        <button onclick="startDownload()" id="downloadBtn">
            تحميل 🚀
        </button>
        
        <div id="message" class="message"></div>
        
        <div class="footer">
            <p class="footer-text">Developed by <span class="footer-name">Hosam Elsayed</span></p>
        </div>
    </div>
    
    <script>
        function startDownload() {
            const url = document.getElementById('url').value.trim();
            const messageDiv = document.getElementById('message');
            const downloadBtn = document.getElementById('downloadBtn');
            
            if (!url) {
                messageDiv.className = 'message error';
                messageDiv.textContent = '⚠️ من فضلك أدخل رابط الفيديو';
                return;
            }
            
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '⏳ جاري التحميل... <span class="spinner"></span>';
            messageDiv.className = 'message loading';
            messageDiv.innerHTML = '📥 جاري معالجة الفيديو وتحميله بليستة أفضل جودة...';
            
            fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'url=' + encodeURIComponent(url)
            })
            .then(response => response.json())
            .then(data => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = 'تحميل 🚀';
                
                if (data.success) {
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = `
                        ✅ تم تجهيز الفيديو بنجاح!
                        <br>📁 ${data.filename}
                        <br>📏 الحجم: ${data.size}
                        <br><a href="/get-file/${data.file_id}" class="download-btn" download>📥 اضغط هنا للتحميل المباشر</a>
                    `;
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = '❌ ' + (data.error || 'فشل التحميل');
                }
            })
            .catch(error => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = 'تحميل 🚀';
                messageDiv.className = 'message error';
                messageDiv.textContent = '❌ حدث خطأ في الاتصال بالسيرفر';
            });
        }
    </script>
</body>
</html>
'''

prepared_files = {}

def cleanup_old_files():
    while True:
        time.sleep(600)
        current_time = time.time()
        to_delete = []
        for file_id, info in list(prepared_files.items()):
            if current_time - info['created_at'] > 1800:
                try:
                    if os.path.exists(info['path']):
                        os.remove(info['path'])
                    to_delete.append(file_id)
                except:
                    pass
        for file_id in to_delete:
            if file_id in prepared_files:
                del prepared_files[file_id]

cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'من فضلك أدخل رابط الفيديو'})
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # إعداد اختيار أفضل جودة مدمجة فوراً بدون تعقيدات
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(temp_dir, '%(title).100s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': True,
            'nocheckcertificate': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'web']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                base = filename.rsplit('.', 1)[0]
                for ext in ['mp4', 'mkv', 'webm']:
                    test_path = f"{base}.{ext}"
                    if os.path.exists(test_path):
                        filename = test_path
                        break
            
            permanent_dir = 'downloaded_files'
            if not os.path.exists(permanent_dir):
                os.makedirs(permanent_dir)
            
            file_id = str(abs(hash(filename + url + str(time.time()))))[:12]
            final_path = os.path.join(permanent_dir, f"{file_id}.mp4")
            shutil.copy2(filename, final_path)
            
            file_size = os.path.getsize(final_path)
            if file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            prepared_files[file_id] = {
                'path': final_path,
                'filename': os.path.basename(filename),
                'size': size_str,
                'created_at': time.time()
            }
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': os.path.basename(filename),
                'size': size_str,
                'title': info.get('title', 'Unknown')[:100]
            })
            
    except Exception as e:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        return jsonify({'success': False, 'error': f'فشل التحميل: {str(e)[:200]}'})

@app.route('/get-file/<file_id>')
def get_file(file_id):
    file_info = prepared_files.get(file_id)
    
    if not file_info or not os.path.exists(file_info['path']):
        return 'الملف غير موجود أو تم حذفه تلقائياً من السيرفر', 404
    
    response = send_file(
        file_info['path'],
        as_attachment=True,
        download_name=file_info['filename']
    )
    
    def delete_after_send():
        time.sleep(5)
        try:
            if os.path.exists(file_info['path']):
                os.remove(file_info['path'])
            if file_id in prepared_files:
                del prepared_files[file_id]
        except:
            pass
    
    threading.Thread(target=delete_after_send, daemon=True).start()
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
