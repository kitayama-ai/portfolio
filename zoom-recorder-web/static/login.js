document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('username', data.username);
            window.location.href = '/';
        } else {
            errorMessage.textContent = data.detail || 'ログインに失敗しました';
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        errorMessage.textContent = 'エラー: ' + error.message;
        errorMessage.style.display = 'block';
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const errorMessage = document.getElementById('errorMessage');
    
    try {
        const response = await fetch('/api/auth/register', {
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
