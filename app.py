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
            font-size: 50px;
            margin-bottom: 10px;
            filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.3));
        }
        
        h1 {
            text-align: center;
            color: var(--gold);
            margin-bottom: 8px;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        
        .subtitle {
            text-align: center;
            color: var(--text-muted);
            margin-bottom: 25px;
            font-size: 13px;
        }
        
        .input-group {
            margin-bottom: 18px;
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
        
        .download-btn-main {
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
        
        .download-btn-main:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        }
        
        .download-btn-main:active {
            transform: translateY(0);
        }
        
        .download-btn-main:disabled {
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
        
        .download-link-btn {
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
        
        .download-link-btn:hover {
            background: var(--gold-light);
            box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);
        }
        
        .quality-section {
            margin: 15px 0;
            display: none;
        }
        
        .quality-title {
            color: var(--gold);
            text-align: center;
            margin-bottom: 10px;
            font-size: 14px;
            font-weight: bold;
        }
        
        .quality-options {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
            max-height: 220px;
            overflow-y: auto;
            padding: 5px;
        }
        
        .quality-btn {
            background: var(--black-lighter);
            color: var(--gold);
            border: 1px solid rgba(212, 175, 55, 0.3);
            padding: 10px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.3s;
            min-width: 85px;
            text-align: center;
        }
        
        .quality-btn:hover {
            background: rgba(212, 175, 55, 0.15);
            border-color: var(--gold);
        }
        
        .quality-btn.selected {
            background: var(--gold);
            color: var(--black);
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            margin-top: 25px;
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
        <p class="subtitle">حمل من أي منصة بأفضل جودة</p>
        
        <div class="input-group">
            <span class="input-icon">🔗</span>
            <input type="text" id="url" placeholder="الصق رابط الفيديو هنا..." />
        </div>
        
        <div class="quality-section" id="qualitySection">
            <p class="quality-title">اختر الجودة:</p>
            <div class="quality-options" id="qualityOptions"></div>
        </div>
        
        <button class="download-btn-main" onclick="startDownload()" id="downloadBtn">
            تحميل 🚀
        </button>
        
        <div id="message" class="message"></div>
        
        <div class="footer">
            <p class="footer-text">Developed by <span class="footer-name">Hosam Elsayed</span></p>
        </div>
    </div>
    
    <script>
        let selectedQuality = 'best';
        
        function selectQuality(formatId, element) {
            document.querySelectorAll('.quality-btn').forEach(btn => btn.classList.remove('selected'));
            element.classList.add('selected');
            selectedQuality = formatId;
        }
        
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
            downloadBtn.innerHTML = '⏳ جاري الفحص... <span class="spinner"></span>';
            messageDiv.className = 'message loading';
            messageDiv.innerHTML = '🔍 جاري فحص الرابط واستخراج الجودات...';
            
            fetch('/get-formats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'url=' + encodeURIComponent(url)
            })
            .then(response => response.json())
            .then(data => {
                downloadBtn.disabled = false;
                
                if (data.success && data.formats && data.formats.length > 1) {
                    showQualityOptions(data.formats);
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = '✅ تم العثور على الفيديو! اختر الجودة ثم اضغط تحميل';
                    downloadBtn.innerHTML = 'تحميل 🚀';
                    downloadBtn.onclick = downloadWithQuality;
                } else if (data.success) {
                    messageDiv.className = 'message loading';
                    messageDiv.innerHTML = '⏳ جاري التحميل المباشر...';
                    proceedDownload(url, selectedQuality);
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = '❌ ' + (data.error || 'خطأ غير معروف');
                    downloadBtn.innerHTML = 'تحميل 🚀';
                    downloadBtn.onclick = startDownload;
                }
            })
            .catch(error => {
                downloadBtn.disabled = false;
                messageDiv.className = 'message error';
                messageDiv.textContent = '❌ حدث خطأ في الاتصال';
                downloadBtn.innerHTML = 'تحميل 🚀';
                downloadBtn.onclick = startDownload;
            });
        }
        
        function showQualityOptions(formats) {
            const section = document.getElementById('qualitySection');
            const options = document.getElementById('qualityOptions');
            section.style.display = 'block';
            options.innerHTML = '';
            
            formats.forEach((format, index) => {
                const btn = document.createElement('button');
                btn.className = 'quality-btn' + (index === 0 ? ' selected' : '');
                btn.textContent = format.label;
                btn.onclick = function() { selectQuality(format.id, this); };
                options.appendChild(btn);
            });
            
            if (formats.length > 0) {
                selectedQuality = formats[0].id;
            }
        }
        
        function downloadWithQuality() {
            const url = document.getElementById('url').value.trim();
            if (!url) return;
            proceedDownload(url, selectedQuality);
        }
        
        function proceedDownload(url, quality) {
            const messageDiv = document.getElementById('message');
            const downloadBtn = document.getElementById('downloadBtn');
            
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '⏳ جاري التحميل... <span class="spinner"></span>';
            messageDiv.className = 'message loading';
            messageDiv.innerHTML = '📥 جاري تحميل الفيديو من السيرفر...';
            
            fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'url=' + encodeURIComponent(url) + '&format=' + quality
            })
            .then(response => response.json())
            .then(data => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = 'تحميل 🚀';
                downloadBtn.onclick = startDownload;
                
                if (data.success) {
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = `
                        ✅ تم التجهيز!
                        <br>📁 ${data.filename}
                        <br>📏 ${data.size}
                        <br><a href="/get-file/${data.file_id}" class="download-link-btn" download>📥 تحميل الآن</a>
                    `;
                    document.getElementById('qualitySection').style.display = 'none';
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = '❌ ' + (data.error || 'فشل التحميل');
                }
            })
            .catch(error => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = 'تحميل 🚀';
                downloadBtn.onclick = startDownload;
                messageDiv.className = 'message error';
                messageDiv.textContent = '❌ حدث خطأ في الاتصال';
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

@app.route('/get-formats', methods=['POST'])
def get_formats():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'من فضلك أدخل رابط الفيديو'})
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            seen_resolutions = set()
            
            for f in info.get('formats', []):
                height = f.get('height')
                if height and f.get('vcodec') != 'none':
                    if height not in seen_resolutions:
                        seen_resolutions.add(height)
                        has_audio = f.get('acodec') != 'none'
                        filesize = f.get('filesize')
                        size_str = ''
                        if filesize:
                            if filesize < 1024 * 1024:
                                size_str = f"({filesize/1024:.0f}KB)"
                            elif filesize < 100 * 1024 * 1024:
                                size_str = f"({filesize/(1024*1024):.0f}MB)"
                            else:
                                size_str = "(حجم كبير)"
                        
                        audio_icon = '🔊' if has_audio else '🔇'
                        formats.append({
                            'id': f"{f['format_id']}+bestaudio/best",
                            'label': f"{audio_icon} {height}p {size_str}",
                            'quality': f"{height}p"
                        })
            
            formats.sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
            
            if not formats:
                formats = [{'id': 'best[ext=mp4]/best', 'label': '🎬 أفضل جودة متاحة', 'quality': 'best'}]
            
            return jsonify({
                'success': True,
                'formats': formats[:10],
                'title': info.get('title', 'Unknown')[:100]
            })
                
    except Exception as e:
        return jsonify({'success': False, 'error': f'خطأ: {str(e)[:200]}'})

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_id = request.form.get('format', 'best')
    
    if not url:
        return jsonify({'success': False, 'error': 'من فضلك أدخل رابط الفيديو'})
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        ydl_opts = {
            'format': format_id if format_id != 'best' else 'best[ext=mp4]/best',
            'outtmpl': os.path.join(temp_dir, '%(title).100s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                base = filename.rsplit('.', 1)[0]
                for ext in ['mp4', 'webm', 'mkv']:
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
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
            
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
