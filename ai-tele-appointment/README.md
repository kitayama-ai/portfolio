# AIテレアポ部隊 (AI Tele-Appointment System)

## 概要
コンテンツビジネスの「Zoomアポ取り」を自動化するシステム。
LPで電話番号を登録した直後に、AI（Vapi）が自動で電話をかけ、アポを確定させる「Speed to Lead」モデルを実現する。

## システム構成

### 1. Frontend (LP)
- **機能**: ユーザーへのオファー提示（動画など）、電話番号入力フォーム。
- **要件**:
  - 電話番号入力必須（SMS送信同意を含む）。
  - 送信後、サンクスページへ遷移（VSL動画再生）。

### 2. Backend (Control Server)
- **技術**: Python (FastAPI)
- **機能**:
  - LPからのフォームデータ受信 (Webhook受け口)。
  - Vapi APIへの架電リクエスト送信。
  - CRM/Google Sheetsへの顧客情報保存（オプション）。

### 3. AI Voice (Vapi)
- **役割**: 架電、ヒアリング、アポ日程調整。
- **連携**: バックエンドからのAPIリクエストで起動。

## フロー
1. ユーザーがLPで電話番号を入力し「動画を見る」ボタンを押下。
2. バックエンドがデータを受信。
3. バックエンドがVapi APIをコールし、登録された電話番号へ即時架電。
4. ユーザーの電話が鳴る（LPで動画を見ている最中）。
5. AIが通話開始、アポを打診。

## 技術スタック
- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **External API**: Vapi API
- **Deployment**: Render / Railway (想定)

## 今後の拡張
- カレンダー連携 (Calendly / Google Calendar)
- SMS送信連携 (Twilio)
