from flask import Flask, request, jsonify, send_file
from TTS.api import TTS
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Load model
print("⏳ TTS Model load ho raha hai...")
try:
    tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", gpu=False)
    print("✅ Model ready!")
except Exception as e:
    print(f"Error loading model: {e}")
    tts = None

VOICE_DIR = "/tmp/voices"
os.makedirs(VOICE_DIR, exist_ok=True)

@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    if tts is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.json
    text = data.get('text', '')
    
    if not text or len(text) > 50000:
        return jsonify({'error': 'Text too long or empty'}), 400
    
    file_id = str(uuid.uuid4())
    output_path = f"{VOICE_DIR}/{file_id}.wav"
    
    try:
        print(f"[{datetime.now()}] Synthesizing: {text[:50]}...")
        tts.tts_to_file(text=text, file_path=output_path)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'download_url': f'/api/download/{file_id}'
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_id>')
def download(file_id):
    file_path = f"{VOICE_DIR}/{file_id}.wav"
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='audio/wav', as_attachment=True, 
                        download_name=f'voiceover_{file_id[:8]}.wav')
    return jsonify({'error': 'File not found'}), 404

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Free TTS Voiceover Generator</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 750px;
                width: 100%;
                padding: 50px;
            }
            
            h1 { 
                color: #333;
                margin-bottom: 10px;
                text-align: center;
                font-size: 32px;
                font-weight: bold;
            }
            
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 35px;
                font-size: 15px;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
                font-size: 14px;
            }
            
            textarea {
                width: 100%;
                height: 220px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 15px;
                font-family: 'Segoe UI', Arial;
                resize: vertical;
                transition: all 0.3s;
            }
            
            textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .char-count {
                text-align: right;
                color: #999;
                font-size: 12px;
                margin-top: 5px;
            }
            
            .button-group {
                display: flex;
                gap: 12px;
                margin-top: 25px;
            }
            
            button {
                flex: 1;
                padding: 14px 24px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                border: none;
                border-radius: 10px;
                transition: all 0.3s;
            }
            
            .generate-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .generate-btn:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }
            
            .generate-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .clear-btn {
                background: #f0f0f0;
                color: #333;
            }
            
            .clear-btn:hover {
                background: #e0e0e0;
            }
            
            .result {
                margin-top: 35px;
                padding: 25px;
                border-radius: 10px;
                display: none;
            }
            
            .result.show { display: block; animation: slideIn 0.3s ease; }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .result.success {
                background: #d4edda;
                border-left: 5px solid #28a745;
            }
            
            .result.error {
                background: #f8d7da;
                border-left: 5px solid #dc3545;
                color: #721c24;
            }
            
            .result h3 {
                margin-bottom: 15px;
                font-size: 18px;
            }
            
            audio {
                width: 100%;
                margin: 20px 0;
                height: 45px;
                border-radius: 8px;
            }
            
            .download-btn {
                background: #28a745;
                color: white;
                padding: 12px 24px;
                display: inline-block;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s;
                border: none;
                cursor: pointer;
            }
            
            .download-btn:hover {
                background: #218838;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
            }
            
            .loading {
                text-align: center;
                color: #667eea;
                font-weight: 600;
                font-size: 16px;
            }
            
            .loading::after {
                content: '';
                animation: dots 1.5s infinite;
            }
            
            @keyframes dots {
                0%, 20% { content: ''; }
                40% { content: '.'; }
                60% { content: '..'; }
                80%, 100% { content: '...'; }
            }
            
            .info-box {
                background: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 12px 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                font-size: 13px;
                color: #0c5aa0;
            }
            
            @media (max-width: 600px) {
                .container { padding: 30px 20px; }
                h1 { font-size: 24px; }
                button { padding: 12px 16px; font-size: 15px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Free TTS Voiceover</h1>
            <p class="subtitle">Text ko natural speech mein badlo - Bilkul Free</p>
            
            <div class="info-box">
                ℹ️ First time pe 1-2 minutes lag sakte hain. Baad mein 30-60 seconds mein done.
            </div>
            
            <div class="form-group">
                <label for="text">Apna Text Likho:</label>
                <textarea id="text" placeholder="Yahan text paste karo..."></textarea>
                <div class="char-count"><span id="charCount">0</span> / 50000 characters</div>
            </div>
            
            <div class="button-group">
                <button class="generate-btn" onclick="synthesize()" id="genBtn">🎬 Generate Audio</button>
                <button class="clear-btn" onclick="clearText()">Clear</button>
            </div>
            
            <div id="result" class="result"></div>
        </div>
        
        <script>
            const textArea = document.getElementById('text');
            const charCount = document.getElementById('charCount');
            
            textArea.addEventListener('input', function() {
                charCount.textContent = this.value.length;
            });
            
            function clearText() {
                textArea.value = '';
                charCount.textContent = '0';
                document.getElementById('result').className = 'result';
            }
            
            async function synthesize() {
                const text = document.getElementById('text').value.trim();
                const btn = document.getElementById('genBtn');
                const resultDiv = document.getElementById('result');
                
                if (!text) {
                    alert('Text likho pehle!');
                    return;
                }
                
                btn.disabled = true;
                resultDiv.className = 'result show loading';
                resultDiv.innerHTML = '<p>⏳ Audio generate ho raha hai</p>';
                
                try {
                    const response = await fetch('/api/synthesize', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.className = 'result show success';
                        resultDiv.innerHTML = `
                            <h3>✅ Tayyar ho gaya!</h3>
                            <audio controls>
                                <source src="${data.download_url}" type="audio/wav">
                            </audio>
                            <br>
                            <button class="download-btn" onclick="downloadAudio('${data.download_url}')">
                                ⬇️ Download Audio
                            </button>
                        `;
                    } else {
                        resultDiv.className = 'result show error';
                        resultDiv.innerHTML = `<h3>❌ Error</h3><p>${data.error || 'Kuch ghalat hua'}</p>`;
                    }
                } catch (err) {
                    resultDiv.className = 'result show error';
                    resultDiv.innerHTML = `<h3>❌ Error</h3><p>${err.message}</p>`;
                } finally {
                    btn.disabled = false;
                }
            }
            
            function downloadAudio(url) {
                const a = document.createElement('a');
                a.href = url;
                a.download = 'voiceover.wav';
                a.click();
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
