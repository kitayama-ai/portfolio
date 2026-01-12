const API_BASE = '/api';
let authToken = localStorage.getItem('authToken');

// 認証チェック
if (!authToken) {
    window.location.href = '/login.html';
}

// API呼び出し
async function apiCall(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        logout();
        return;
    }
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'エラーが発生しました');
    }
    
    return response.json();
}

// タブ切り替え
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(`${tabName}Tab`).classList.add('active');
    event.target.classList.add('active');
}

// コース一覧を読み込み
async function loadCourses() {
    try {
        const data = await apiCall('/courses');
        const coursesList = document.getElementById('coursesList');
        const courseSelect = document.getElementById('courseSelect');
        const courseFilter = document.getElementById('courseFilter');
        
        coursesList.innerHTML = '';
        courseSelect.innerHTML = '<option value="">コースを選択</option>';
        courseFilter.innerHTML = '<option value="">全コース</option>';
        
        data.courses.forEach(course => {
            // コース一覧
            const courseItem = document.createElement('div');
            courseItem.className = 'course-item';
            courseItem.innerHTML = `
                <div>
                    <strong>${course.course_name}</strong> (${course.course_id})
                    ${course.manager_slack_id ? `<br><small>担当者: ${course.manager_slack_id}</small>` : ''}
                </div>
            `;
            coursesList.appendChild(courseItem);
            
            // セレクトボックスに追加
            const option1 = document.createElement('option');
            option1.value = course.course_id;
            option1.textContent = course.course_name;
            courseSelect.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = course.course_id;
            option2.textContent = course.course_name;
            courseFilter.appendChild(option2);
        });
    } catch (error) {
        alert('コース一覧の読み込みに失敗しました: ' + error.message);
    }
}

// コース登録モーダルを開く
function openCourseModal() {
    document.getElementById('courseModal').style.display = 'block';
}

// コース登録モーダルを閉じる
function closeCourseModal() {
    document.getElementById('courseModal').style.display = 'none';
    document.getElementById('courseForm').reset();
}

// コースを登録
async function registerCourse(event) {
    event.preventDefault();
    
    const courseId = document.getElementById('courseId').value;
    const courseName = document.getElementById('courseName').value;
    const managerSlackId = document.getElementById('managerSlackId').value;
    
    try {
        await apiCall('/courses/register', {
            method: 'POST',
            body: JSON.stringify({
                course_id: courseId,
                course_name: courseName,
                manager_slack_id: managerSlackId || null
            })
        });
        
        alert('コースを登録しました');
        closeCourseModal();
        loadCourses();
    } catch (error) {
        alert('コース登録に失敗しました: ' + error.message);
    }
}

// 会話履歴を読み込み
async function loadConversations() {
    try {
        const courseId = document.getElementById('courseFilter').value;
        const limit = parseInt(document.getElementById('limitInput').value) || 100;
        
        const data = await apiCall(`/conversations?course_id=${courseId || ''}&limit=${limit}`);
        const conversationsList = document.getElementById('conversationsList');
        
        conversationsList.innerHTML = '';
        
        if (data.conversations.length === 0) {
            conversationsList.innerHTML = '<p>会話履歴がありません</p>';
            return;
        }
        
        data.conversations.forEach(conv => {
            const convItem = document.createElement('div');
            convItem.className = 'conversation-item';
            
            const satisfactionClass = conv.is_satisfied ? 'satisfied' : 'unsatisfied';
            const needsReview = conv.needs_human_review ? '<span class="needs-review">要レビュー</span>' : '';
            
            convItem.innerHTML = `
                <div class="conversation-header">
                    <span>${conv.datetime} | ${conv.user_id} | ${conv.course_id}</span>
                    <span>
                        <span class="satisfaction-badge ${satisfactionClass}">
                            満足度: ${(conv.satisfaction_score * 100).toFixed(0)}%
                        </span>
                        ${needsReview}
                    </span>
                </div>
                <div class="conversation-message user">
                    <strong>質問:</strong> ${conv.user_message}
                </div>
                <div class="conversation-message bot">
                    <strong>回答:</strong> ${conv.bot_response}
                </div>
                ${conv.improvement_comment ? `
                    <div class="conversation-message">
                        <strong>改善コメント:</strong> ${conv.improvement_comment}
                    </div>
                ` : ''}
            `;
            conversationsList.appendChild(convItem);
        });
    } catch (error) {
        alert('会話履歴の読み込みに失敗しました: ' + error.message);
    }
}

// PDFをアップロード
async function uploadPDF() {
    const courseId = document.getElementById('courseSelect').value;
    const fileInput = document.getElementById('pdfFile');
    
    if (!courseId) {
        alert('コースを選択してください');
        return;
    }
    
    if (!fileInput.files[0]) {
        alert('PDFファイルを選択してください');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/courses/${courseId}/pdf`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'アップロードに失敗しました');
        }
        
        const data = await response.json();
        document.getElementById('uploadStatus').innerHTML = `
            <div style="padding: 10px; background: #d4edda; color: #155724; border-radius: 4px; margin-top: 10px;">
                PDFをアップロードしました！<br>
                チャンク数: ${data.data.chunk_count}, テキスト長: ${data.data.text_length}
            </div>
        `;
        fileInput.value = '';
    } catch (error) {
        alert('PDFアップロードに失敗しました: ' + error.message);
    }
}

// ログアウト
function logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/login.html';
}

// モーダル外クリックで閉じる
window.onclick = function(event) {
    const modal = document.getElementById('courseModal');
    if (event.target === modal) {
        closeCourseModal();
    }
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadCourses();
    loadConversations();
});
