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
            padding: 40px 30px;
            box-shadow: 
                0 20px 60px rgba(0,0,0,0.5),
                0 0 0 1px rgba(212, 175, 55, 0.1),
                0 0 40px rgba(212, 175, 55, 0.05);
            max-width: 520px;
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
            margin-bottom: 5px;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        
        .subtitle {
            text-align: center;
            color: var(--text-muted);
            margin-bottom: 25px;
            font-size: 13px;
            letter-spacing: 0.5px;
        }
        
        .platforms {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .platform {
            background: var(--black-lighter);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            color: var(--gold);
            border: 1px solid rgba(212, 175, 55, 0.2);
            transition: all 0.3s;
        }
        
        .platform:hover {
            background: rgba(212, 175, 55, 0.1);
            border-color: var(--gold);
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
            position: relative;
            overflow: hidden;
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
            margin-top: 20px;
            padding: 16px;
            border-radius: 14px;
            text-align: center;
            display: none;
            font-size: 14px;
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
            margin-top: 12px;
            transition: all 0.3s;
            letter-spacing: 0.5px;
        }
        
        .download-btn:hover {
            background: var(--gold-light);
            box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);
        }
        
        .quality-options {
            margin-top: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
        }
        
        .quality-btn {
            background: var(--black-lighter);
            color: var(--gold);
            border: 1px solid rgba(212, 175, 55, 0.3);
            padding: 8px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
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
        
        .type-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 18px;
        }
        
        .type-btn {
            flex: 1;
            padding: 12px;
            background: var(--black-lighter);
            color: var(--text-muted);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 12px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            text-align: center;
        }
        
        .type-btn.active {
            background: rgba(212, 175, 55, 0.15);
            color: var(--gold);
            border-color: var(--gold);
        }
        
        .footer {
            text-align: center;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid rgba(212, 175, 55, 0.1);
        }
        
        .footer-text {
            color: var(--text-muted);
            font-size: 12px;
            letter-spacing: 1px;
        }
        
        .footer-name {
            color: var(--gold);
            font-weight: bold;
            font-size: 13px;
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
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
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 1.5s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-icon">🎥</div>
        <h1>محمل الفيديوهات</h1>
        <p class="subtitle">حمل من أي منصة بجودة تختارها بنفسك</p>
        
        <div class="platforms">
            <span class="platform">YouTube</span>
            <span class="platform">TikTok</span>
            <span class="platform">Instagram</span>
            <span class="platform">Facebook</span>
            <span class="platform">Twitter</span>
            <span class="platform">+1500 موقع</span>
        </div>
        
        <div class="type-selector">
            <button class="type-btn active" onclick="setType('video')" id="btn-video">
                🎬 فيديو
            </button>
            <button class="type-btn" onclick="setType('audio')" id="btn-audio">
                🎵 صوت MP3
            </button>
        </div>
        
        <div class="input-group">
            <span class="input-icon">🔗</span>
            <input type="text" id="url" placeholder="الصق رابط الفيديو هنا..." />
        </div>
        
        <div id="qualitySection" style="display:none;">
            <p style="color: var(--gold); text-align: center; margin-bottom: 10px; font-size: 13px;">
                اختر الجودة:
            </p>
            <div class="quality-options" id="qualityOptions"></div>
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
        let downloadType = 'video';
        let selectedQuality = 'best';
        let availableFormats = [];
        
        function setType(type) {
            downloadType = type;
            document.getElementById('btn-video').classList.toggle('active', type === 'video');
            document.getElementById('btn-audio').classList.toggle('active', type === 'audio');
            
            if (type === 'audio') {
                document.getElementById('qualitySection').style.display = 'none';
                selectedQuality = 'bestaudio';
            } else {
                document.getElementById('qualitySection').style.display = 'none';
                selectedQuality = 'best';
            }
        }
        
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
            messageDiv.innerHTML = '🔍 جاري فحص الرابط واستخراج الجودات المتاحة...';
            
            // أولاً: نجيب الجودات المتاحة
            fetch('/get-formats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'url=' + encodeURIComponent(url) + '&type=' + downloadType
            })
            .then(response => response.json())
            .then(data => {
                downloadBtn.disabled = false;
                
                if (data.success && data.formats && data.formats.length > 0) {
                    // فيه جودات متعددة - نعرضها للمستخدم
                    availableFormats = data.formats;
                    showQualityOptions(data.formats, data.title);
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = '✅ تم العثور على الفيديو! اختر الجودة المناسبة ثم اضغط تحميل.';
                    downloadBtn.innerHTML = 'تحميل 🚀';
                    downloadBtn.onclick = downloadWithQuality;
                } else if (data.success) {
                    // مفيش جودات متعددة - تحميل مباشر
                    messageDiv.className = 'message loading';
                    messageDiv.innerHTML = '⏳ جاري التحميل المباشر...';
                    proceedDownload(url, selectedQuality, downloadType);
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = '❌ ' + (data.error || 'لم يتم العثور على صيغ متاحة');
                    downloadBtn.innerHTML = 'تحميل 🚀';
                    downloadBtn.onclick = startDownload;
                }
            })
            .catch(error => {
                downloadBtn.disabled = false;
                messageDiv.className = 'message error';
                messageDiv.textContent = '❌ حدث خطأ في الاتصال بالخادم';
                downloadBtn.innerHTML = 'تحميل 🚀';
                downloadBtn.onclick = startDownload;
            });
        }
        
        function showQualityOptions(formats, title) {
            const qualitySection = document.getElementById('qualitySection');
            const qualityOptions = document.getElementById('qualityOptions');
            
            qualitySection.style.display = 'block';
            qualityOptions.innerHTML = '';
            
            formats.forEach((format, index) => {
                const btn = document.createElement('button');
                btn.className = 'quality-btn' + (index === 0 ? ' selected' : '');
                btn.textContent = format.label;
                btn.onclick = function() { selectQuality(format.id, this); };
                qualityOptions.appendChild(btn);
            });
            
            if (formats.length > 0) {
                selectedQuality = formats[0].id;
            }
        }
        
        function downloadWithQuality() {
            const url = document.getElementById('url').value.trim();
            const messageDiv = document.getElementById('message');
            const downloadBtn = document.getElementById('downloadBtn');
            
            if (!url) return;
            
            proceedDownload(url, selectedQuality, downloadType);
        }
        
        function proceedDownload(url, quality, type) {
            const messageDiv = document.getElementById('message');
            const downloadBtn = document.getElementById('downloadBtn');
            
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '⏳ جاري التحميل... <span class="spinner"></span>';
            messageDiv.className = 'message loading';
            messageDiv.innerHTML = '📥 جاري تحميل الفيديو من السيرفر...';
            
            fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'url=' + encodeURIComponent(url) + '&format=' + quality + '&type=' + type
            })
            .then(response => response.json())
            .then(data => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = 'تحميل 🚀';
                downloadBtn.onclick = startDownload;
                
                if (data.success) {
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = `
                        ✅ تم تجهيز الملف بنجاح!
                        <br>
                        📁 ${data.filename}
                        <br>
                        📏 ${data.size}
                        <br>
                        <a href="/get-file/${data.file_id}" class="download-btn" download>
                            📥 تحميل الآن
                        </a>
                    `;
                    
                    // إخفاء خيارات الجودة
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
                messageDiv.textContent = '❌ حدث خطأ في الاتصال بالخادم';
            });
        }
    </script>
</body>
</html>
'''

# تخزين الملفات المجهزة مع وقت الإنشاء للحذف التلقائي
prepared_files = {}

def cleanup_old_files():
    """حذف الملفات القديمة كل 10 دقائق"""
    while True:
        time.sleep(600)  # كل 10 دقائق
        current_time = time.time()
        to_delete = []
        for file_id, info in prepared_files.items():
            if current_time - info['created_at'] > 1800:  # 30 دقيقة
                try:
                    if os.path.exists(info['path']):
                        os.remove(info['path'])
                    to_delete.append(file_id)
                except:
                    pass
        for file_id in to_delete:
            del prepared_files[file_id]

# بدء خيط التنظيف في الخلفية
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-formats', methods=['POST'])
def get_formats():
    """استخراج الجودات المتاحة للفيديو"""
    url = request.form.get('url')
    download_type = request.form.get('type', 'video')
    
    if not url:
        return jsonify({'success': False, 'error': 'من فضلك أدخل رابط الفيديو'})
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if download_type == 'audio':
                # للصوت - نرجع صيغ الصوت فقط
                formats = []
                for f in info.get('formats', []):
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        abr = f.get('abr', 0)
                        if abr:
                            formats.append({
                                'id': f['format_id'],
                                'label': f"🎵 {f.get('format_note', 'Audio')} - {int(abr)}kbps",
                                'quality': f"{int(abr)}kbps"
                            })
                
                if not formats:
                    formats.append({
                        'id': 'bestaudio/best',
                        'label': '🎵 أفضل جودة صوت متاحة',
                        'quality': 'best'
                    })
                
                return jsonify({
                    'success': True,
                    'formats': formats[:8],
                    'title': info.get('title', 'Unknown')[:100],
                    'type': 'audio'
                })
            else:
                # للفيديو - نرجع الجودات المختلفة
                formats = []
                seen_resolutions = set()
                
                for f in info.get('formats', []):
                    height = f.get('height')
                    if height and f.get('ext') == 'mp4' and f.get('vcodec') != 'none':
                        if height not in seen_resolutions:
                            seen_resolutions.add(height)
                            has_audio = f.get('acodec') != 'none'
                            filesize = f.get('filesize')
                            size_str = ''
                            if filesize:
                                if filesize < 1024 * 1024:
                                    size_str = f"({filesize/1024:.0f}KB)"
                                elif filesize < 50 * 1024 * 1024:
                                    size_str = f"({filesize/(1024*1024):.0f}MB)"
                                else:
                                    size_str = "(حجم كبير)"
                            
                            audio_icon = '🔊' if has_audio else '🔇'
                            formats.append({
                                'id': f['format_id'],
                                'label': f"{audio_icon} {height}p {size_str}",
                                'quality': f"{height}p"
                            })
                
                # ترتيب الجودات من الأعلى للأقل
                formats.sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
                
                if formats:
                    return jsonify({
                        'success': True,
                        'formats': formats[:10],
                        'title': info.get('title', 'Unknown')[:100],
                        'type': 'video'
                    })
                else:
                    return jsonify({
                        'success': True,
                        'formats': [{'id': 'best', 'label': '🎬 أفضل جودة متاحة', 'quality': 'best'}],
                        'title': info.get('title', 'Unknown')[:100],
                        'type': 'video'
                    })
                
    except Exception as e:
        return jsonify({'success': False, 'error': f'فشل استخراج المعلومات: {str(e)[:150]}'})

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_id = request.form.get('format', 'best')
    download_type = request.form.get('type', 'video')
    
    if not url:
        return jsonify({'success': False, 'error': 'من فضلك أدخل رابط الفيديو'})
    
    try:
        temp_dir = tempfile.mkdtemp()
        
        if download_type == 'audio':
            # تحميل الصوت وتحويله لـ MP3
            ydl_opts = {
                'format': format_id if format_id != 'bestaudio' else 'bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title).100s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'restrictfilenames': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            # تحميل الفيديو
            ydl_opts = {
                'format': format_id if format_id != 'best' else 'best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, '%(title).100s.%(ext)s'),
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
                'restrictfilenames': True,
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # البحث عن الملف الناتج (قد يتغير الامتداد بعد المعالجة)
            if not os.path.exists(filename):
                base = filename.rsplit('.', 1)[0]
                for ext in (['mp3', 'm4a', 'webm', 'opus'] if download_type == 'audio' else ['mp4', 'webm', 'mkv']):
                    test_path = f"{base}.{ext}"
                    if os.path.exists(test_path):
                        filename = test_path
                        break
            
            # نقل الملف للمجلد الدائم
            permanent_dir = 'downloaded_files'
            if not os.path.exists(permanent_dir):
                os.makedirs(permanent_dir)
            
            file_id = str(abs(hash(filename + url + str(time.time()))))[:12]
            final_ext = 'mp3' if download_type == 'audio' else 'mp4'
            final_path = os.path.join(permanent_dir, f"{file_id}.{final_ext}")
            shutil.copy2(filename, final_path)
            
            # حساب الحجم
            file_size = os.path.getsize(final_path)
            if file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # تخزين معلومات الملف مع وقت الإنشاء
            prepared_files[file_id] = {
                'path': final_path,
                'filename': os.path.basename(filename if download_type == 'video' else filename.rsplit('.', 1)[0] + '.mp3'),
                'size': size_str,
                'created_at': time.time()
            }
            
            # تنظيف المجلد المؤقت فوراً
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': prepared_files[file_id]['filename'],
                'size': size_str,
                'title': info.get('title', 'Unknown')[:100],
                'type': download_type
            })
            
    except Exception as e:
        # تنظيف في حالة الخطأ
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
    
    # إرسال الملف وحذفه بعد التحميل
    response = send_file(
        file_info['path'],
        as_attachment=True,
        download_name=file_info['filename']
    )
    
    # جدولة الحذف بعد الإرسال
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
