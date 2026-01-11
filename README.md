# Portfolio

自動化・システム開発エンジニアのポートフォリオサイト

## 概要

Pythonを使った業務自動化・システム開発を専門とするエンジニアのポートフォリオサイトです。

## 技術スタック

- HTML/CSS/JavaScript（バニラJS）
- Vercel（ホスティング）

## 実績の追加方法

### 方法1: projects.jsonを編集

`projects.json`ファイルを編集してプロジェクトを追加・更新できます。

```json
{
    "title": "プロジェクト名",
    "description": "プロジェクトの説明",
    "tech": ["技術1", "技術2", "技術3"],
    "github": "https://github.com/username/repo",
    "demo": "https://demo-url.com"
}
```

### 方法2: script.jsを直接編集

`script.js`の`projectsData`配列を編集してプロジェクトを追加・更新できます。

## デプロイ

このリポジトリはVercelに接続しており、GitHubにプッシュすると自動的にデプロイされます。

## ライセンス

MIT License

