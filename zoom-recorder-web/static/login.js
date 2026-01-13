// APIベースURL（環境変数またはデフォルト値）
const API_BASE_URL = window.API_BASE_URL || '';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    const loginButton = document.querySelector('#loginForm button[type="submit"]');
    const loginForm = document.getElementById('loginForm');
    
    // エラーメッセージとローディングメッセージをクリア
    errorMessage.textContent = '';
    errorMessage.style.display = 'none';
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.style.display = 'none';
    }
    
    // ログインボタンを無効化してローディング状態に
    loginButton.disabled = true;
    const originalButtonText = loginButton.textContent;
    loginButton.textContent = 'ログイン中...';
    loginButton.style.opacity = '0.6';
    if (loadingMessage) {
        loadingMessage.style.display = 'block';
    }
    
    try {
        console.log('ログイン試行:', { username, passwordLength: password.length });
        
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        console.log('レスポンスステータス:', response.status);
        
        const data = await response.json();
        console.log('レスポンスデータ:', { ...data, access_token: data.access_token ? '存在' : 'なし' });
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('username', data.username);
            console.log('ログイン成功、リダイレクト中...');
            // フロントエンドのindex.htmlにリダイレクト
            window.location.href = '/frontend/index.html';
        } else {
            console.error('ログイン失敗:', data.detail);
            errorMessage.textContent = data.detail || 'ログインに失敗しました';
            errorMessage.style.display = 'block';
            if (loadingMessage) {
                loadingMessage.style.display = 'none';
            }
            // エラー時にフォームを再び有効化
            loginButton.disabled = false;
            loginButton.textContent = originalButtonText;
            loginButton.style.opacity = '1';
            // パスワードフィールドをクリア
            document.getElementById('password').value = '';
            // パスワードフィールドにフォーカス
            document.getElementById('password').focus();
        }
    } catch (error) {
        console.error('ログインエラー:', error);
        errorMessage.textContent = 'エラー: ' + error.message;
        errorMessage.style.display = 'block';
        if (loadingMessage) {
            loadingMessage.style.display = 'none';
        }
        // エラー時にフォームを再び有効化
        loginButton.disabled = false;
        loginButton.textContent = originalButtonText;
        loginButton.style.opacity = '1';
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const errorMessage = document.getElementById('errorMessage');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('ユーザー登録が完了しました。ログインしてください。');
            closeRegister();
        } else {
            errorMessage.textContent = data.detail || '登録に失敗しました';
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        errorMessage.textContent = 'エラー: ' + error.message;
        errorMessage.style.display = 'block';
    }
});

function showRegister() {
    document.getElementById('registerModal').style.display = 'flex';
}

function closeRegister() {
    document.getElementById('registerModal').style.display = 'none';
}

// モーダル外クリックで閉じる
document.getElementById('registerModal').addEventListener('click', (e) => {
    if (e.target.id === 'registerModal') {
        closeRegister();
    }
});
