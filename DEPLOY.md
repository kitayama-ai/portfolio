# ポートフォリオサイト - デプロイ手順

## Vercelでのデプロイ

### 1. Vercelに接続（既に完了している場合）

Vercelダッシュボードで既に`portfolio`リポジトリが接続されている場合は、自動的にデプロイされます。

### 2. 初回デプロイ

1. Vercelダッシュボードにアクセス: https://vercel.com/dashboard
2. "Add New..." → "Project" を選択
3. "Import Git Repository" を選択
4. `kitayama-ai/portfolio` を選択
5. "Deploy" をクリック

### 3. デプロイ設定

- **Framework Preset**: Other（または自動検出）
- **Root Directory**: `./`（デフォルト）
- **Build Command**: （不要）
- **Output Directory**: `./`（デフォルト）

### 4. カスタムドメイン（オプション）

Vercelダッシュボードでカスタムドメインを設定できます：
1. プロジェクト設定 → Domains
2. ドメインを追加
3. DNS設定を完了

---

## 実績の追加方法

### 方法1: `projects.json`を編集（推奨）

`projects.json`ファイルを編集してプロジェクトを追加・更新できます。

```json
{
    "title": "プロジェクト名",
    "description": "プロジェクトの説明（2-3行で簡潔に）",
    "tech": ["技術1", "技術2", "技術3"],
    "github": "https://github.com/username/repo",
    "demo": "https://demo-url.com"
}
```

### 方法2: `script.js`を直接編集

`script.js`の`projectsData`配列を編集してプロジェクトを追加・更新できます。

```javascript
const projectsData = [
    {
        title: "プロジェクト名",
        description: "プロジェクトの説明",
        tech: ["技術1", "技術2", "技術3"],
        github: "https://github.com/username/repo",
        demo: "https://demo-url.com"
    },
    // ... 他のプロジェクト
];
```

### 実績追加後の作業

1. ファイルを編集
2. Gitにコミット・プッシュ
   ```bash
   git add .
   git commit -m "Add: プロジェクト名を追加"
   git push origin master
   ```
3. Vercelが自動的にデプロイ（数分かかります）

---

## GitHubリポジトリ情報

**リポジトリURL**: https://github.com/kitayama-ai/portfolio

---

## ローカルでの確認

ローカルで確認する場合は、以下のコマンドを実行：

```bash
# シンプルなHTTPサーバーを起動（Python 3の場合）
python -m http.server 8000

# または、Node.jsの場合
npx http-server
```

ブラウザで `http://localhost:8000` にアクセスして確認できます。

