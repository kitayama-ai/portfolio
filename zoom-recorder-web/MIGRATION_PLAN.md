# デプロイ移行プラン

## 現在の計画

### フェーズ1: Railwayで開始（30日間）
- ✅ Railwayでデプロイ
- ✅ 動作確認
- ✅ 30日間無料トライアルを利用

### フェーズ2: Renderへ移行（30日後）
- 📅 30日後にRenderへ移行
- 📝 移行手順: `RENDER_MIGRATION.md` を参照
- 💰 無料プランで継続利用

## 移行タイムライン

```
Day 0  → Railwayでデプロイ開始
Day 30 → Railwayトライアル終了
Day 30 → Renderへ移行開始
Day 31 → Renderで本番運用開始
```

## 移行時のチェックリスト

### 事前準備
- [ ] Renderアカウント作成
- [ ] 環境変数の値をメモ（Railwayから取得）

### 移行当日
- [ ] Renderでプロジェクト作成
- [ ] 設定入力
- [ ] 環境変数設定
- [ ] デプロイ
- [ ] 動作確認
- [ ] Railwayプロジェクトの停止/削除

### 移行後
- [ ] 公開URLの更新（必要に応じて）
- [ ] 動作確認（数日間）

## 参考ドキュメント

- `RENDER_MIGRATION.md` - 詳細な移行手順
- `PRICING_COMPARISON.md` - 料金比較
- `DEPLOY_RECOMMENDED.md` - デプロイ方法の比較
