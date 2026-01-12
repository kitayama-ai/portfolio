class ZoomRecorderApp {
    constructor() {
        // APIベースURL（環境変数またはデフォルト値）
        this.apiBaseUrl = window.API_BASE_URL || '';
        this.wsBaseUrl = window.WS_BASE_URL || '';
        this.token = localStorage.getItem('access_token');
        if (!this.token) {
            window.location.href = '/login.html';
            return;
        }
        this.ws = null;
        this.recordingInterval = null;
        this.startTime = null;
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.loadSettings();
        this.updateStatus();
    }

    connectWebSocket() {
        // WebSocket URL（環境変数または自動検出）
        let wsUrl;
        if (this.wsBaseUrl) {
            wsUrl = this.wsBaseUrl;
        } else {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            wsUrl = `${protocol}//${window.location.host}/ws`;
        }
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.addLog('WebSocket接続を確立しました', 'success');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };

        this.ws.onerror = (error) => {
            this.addLog('WebSocketエラーが発生しました', 'error');
        };

        this.ws.onclose = () => {
            this.addLog('WebSocket接続が切断されました。再接続中...', 'warning');
            setTimeout(() => this.connectWebSocket(), 3000);
        };
    }

    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'status':
            case 'status_update':
                this.updateZoomStatus(message.data);
                break;
            case 'recording_started':
                this.onRecordingStarted(message);
                break;
            case 'recording_stopped':
                this.onRecordingStopped(message);
                break;
            case 'auto_stopped':
                this.onAutoStopped(message);
                break;
            case 'transcription_complete':
                this.addLog(`文字起こし完了（${Math.round(message.duration)}秒）`, 'success');
                break;
            case 'summary_complete':
                this.showSummary(message.summary);
                break;
            case 'document_saved':
                this.addLog(`ドキュメントを保存しました: ${message.title}`, 'success');
                break;
            case 'google_docs_created':
                this.addLog(`Googleドキュメントを作成しました`, 'success');
                this.showGoogleDocsLink(message.url);
                break;
            case 'processing_complete':
                this.addLog(message.message, 'success');
                break;
            case 'error':
                this.addLog(message.message, 'error');
                break;
        }
    }

    setupEventListeners() {
        const recordButton = document.getElementById('recordButton');
        recordButton.addEventListener('click', () => this.toggleRecording());
        
        // 録画モード変更時の処理
        const modeRadios = document.querySelectorAll('input[name="recordingMode"]');
        modeRadios.forEach(radio => {
            radio.addEventListener('change', () => this.onModeChange());
        });
    }

    onModeChange() {
        const selectedMode = document.querySelector('input[name="recordingMode"]:checked').value;
        const audioOnlyLabel = document.getElementById('audioOnlyLabel');
        
        // 録画+文字起こしモードの場合のみ「音声のみ録音」オプションを表示
        if (selectedMode === 'recording_and_transcription') {
            audioOnlyLabel.style.display = 'block';
        } else {
            audioOnlyLabel.style.display = 'none';
            document.getElementById('audioOnlyCheck').checked = false;
        }
    }

    async loadSettings() {
        try {
            const response = await this.apiRequest('/api/settings');
            if (response) {
                const settings = await response.json();
                document.getElementById('recordingFolder').value = settings.recording_folder;
                document.getElementById('documentFolder').value = settings.document_folder;
                document.getElementById('googleDocsCheck').checked = settings.google_docs_enabled;
            }
        } catch (error) {
            console.error('設定読み込みエラー:', error);
        }
    }

    async apiRequest(url, options = {}) {
        // 相対パスの場合はAPIベースURLを追加
        const fullUrl = url.startsWith('http') ? url : `${this.apiBaseUrl}${url}`;
        const headers = {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        const response = await fetch(fullUrl, { ...options, headers });
        
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login.html';
            return null;
        }
        
        return response;
    }

    async updateStatus() {
        try {
            const response = await this.apiRequest('/api/status');
            const data = await response.json();
            
            this.updateUI(data);
        } catch (error) {
            console.error('ステータス取得エラー:', error);
        }
    }

    updateZoomStatus(data) {
        const zoomStatusText = document.getElementById('zoomStatusText');
        const meetingStatusText = document.getElementById('meetingStatusText');
        const recordButton = document.getElementById('recordButton');

        zoomStatusText.textContent = data.zoom_status;
        zoomStatusText.className = `value ${
            data.zoom_status === '会議中' ? 'success' : 
            data.zoom_status === '起動中' ? 'warning' : ''
        }`;

        meetingStatusText.textContent = data.meeting_active ? 'アクティブ' : '非アクティブ';
        meetingStatusText.className = `value ${data.meeting_active ? 'success' : ''}`;

        recordButton.disabled = !data.meeting_active;
    }

    updateUI(data) {
        const statusBadge = document.getElementById('statusBadge');
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const recordButton = document.getElementById('recordButton');
        const recordingInfo = document.getElementById('recordingInfo');

        if (data.recording) {
            statusDot.className = 'status-dot recording';
            statusText.textContent = '録画中';
            recordButton.className = 'btn btn-danger btn-large';
            recordButton.innerHTML = '<span class="btn-icon">⏹️</span><span class="btn-text">録画停止</span>';
            recordingInfo.style.display = 'block';
            
            if (!this.recordingInterval) {
                this.startTime = new Date(data.start_time);
                this.recordingInterval = setInterval(() => this.updateDuration(), 1000);
            }
        } else {
            statusDot.className = 'status-dot waiting';
            statusText.textContent = '待機中';
            recordButton.className = 'btn btn-primary btn-large';
            recordButton.innerHTML = '<span class="btn-icon">🎬</span><span class="btn-text">録画開始</span>';
            recordingInfo.style.display = 'none';
            
            if (this.recordingInterval) {
                clearInterval(this.recordingInterval);
                this.recordingInterval = null;
            }
        }
    }

    updateDuration() {
        if (!this.startTime) return;
        
        const now = new Date();
        const diff = Math.floor((now - this.startTime) / 1000);
        const hours = Math.floor(diff / 3600);
        const minutes = Math.floor((diff % 3600) / 60);
        const seconds = diff % 60;
        
        const durationText = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('recordingDuration').textContent = durationText;
    }

    async toggleRecording() {
        const recordButton = document.getElementById('recordButton');
        const isRecording = recordButton.textContent.includes('停止');

        if (isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        const autoStop = document.getElementById('autoStopCheck').checked;
        const audioOnly = document.getElementById('audioOnlyCheck').checked;
        const selectedMode = document.querySelector('input[name="recordingMode"]:checked').value;

        try {
            const response = await this.apiRequest('/api/recording/start', {
                method: 'POST',
                body: JSON.stringify({
                    auto_stop: autoStop,
                    audio_only: audioOnly && selectedMode === 'recording_and_transcription',
                    mode: selectedMode
                })
            });

            if (response) {
                const data = await response.json();
                
                if (response.ok) {
                    const modeText = selectedMode === 'transcription_only' ? '文字起こし' : '録画';
                    this.addLog(`${modeText}を開始しました`, 'success');
                    this.updateStatus();
                } else {
                    this.addLog(data.detail || '開始に失敗しました', 'error');
                }
            }
        } catch (error) {
            this.addLog('開始エラー: ' + error.message, 'error');
        }
    }

    async stopRecording() {
        try {
            const response = await this.apiRequest('/api/recording/stop', {
                method: 'POST'
            });

            if (response) {
                const data = await response.json();
                
                if (response.ok) {
                    this.addLog('録画を停止しました。処理中...', 'info');
                    this.updateStatus();
                } else {
                    this.addLog(data.detail || '停止に失敗しました', 'error');
                }
            }
        } catch (error) {
            this.addLog('停止エラー: ' + error.message, 'error');
        }
    }

    onRecordingStarted(message) {
        document.getElementById('meetingTitle').textContent = message.meeting_title;
        this.addLog(`録画開始: ${message.meeting_title}`, 'success');
    }

    onRecordingStopped(message) {
        this.addLog(message.message, 'info');
    }

    onAutoStopped(message) {
        this.addLog(message.message, 'success');
    }

    showSummary(summary) {
        const summaryCard = document.getElementById('summaryCard');
        const summaryContent = document.getElementById('summaryContent');
        
        summaryContent.textContent = summary;
        summaryCard.style.display = 'block';
        summaryCard.scrollIntoView({ behavior: 'smooth' });
        
        this.addLog('議事録が生成されました', 'success');
    }

    showGoogleDocsLink(url) {
        const logContainer = document.getElementById('logContainer');
        const logItem = document.createElement('div');
        logItem.className = 'log-item info';
        logItem.innerHTML = `<a href="${url}" target="_blank">📄 Googleドキュメントを開く</a>`;
        logContainer.appendChild(logItem);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    addLog(message, type = 'info') {
        const logContainer = document.getElementById('logContainer');
        const timestamp = new Date().toLocaleTimeString('ja-JP');
        const logItem = document.createElement('div');
        logItem.className = `log-item ${type}`;
        logItem.textContent = `[${timestamp}] ${message}`;
        logContainer.appendChild(logItem);
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

// 設定モーダル関数
function openSettingsModal() {
    document.getElementById('settingsModal').classList.add('active');
}

function closeSettingsModal() {
    document.getElementById('settingsModal').classList.remove('active');
}

async function saveSettings() {
    const recordingFolder = document.getElementById('recordingFolder').value;
    const documentFolder = document.getElementById('documentFolder').value;
    const googleDocsEnabled = document.getElementById('googleDocsCheck').checked;

    try {
        const token = localStorage.getItem('access_token');
        const apiBaseUrl = window.API_BASE_URL || '';
        const response = await fetch(`${apiBaseUrl}/api/settings`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                recording_folder: recordingFolder,
                document_folder: documentFolder,
                google_docs_enabled: googleDocsEnabled
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            alert('設定を保存しました');
            closeSettingsModal();
        } else {
            alert('設定保存エラー: ' + data.detail);
        }
    } catch (error) {
        alert('設定保存エラー: ' + error.message);
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    window.location.href = '/login.html';
}

// モーダル外クリックで閉じる
document.addEventListener('click', (e) => {
    const modal = document.getElementById('settingsModal');
    if (e.target === modal) {
        closeSettingsModal();
    }
});

// アプリを起動
document.addEventListener('DOMContentLoaded', () => {
    new ZoomRecorderApp();
});
