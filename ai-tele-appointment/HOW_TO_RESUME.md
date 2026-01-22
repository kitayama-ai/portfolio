## 開発の再開方法

PCで作業を再開する場合は、以下の手順で行ってください。

### 1. リポジトリの取得（クローン）
まだPCにコードがない場合は、GitHubからリポジトリをクローンします。

```bash
git clone https://github.com/kitayama-ai/portfolio.git
cd portfolio
```

### 2. 作業ブランチへの切り替え
今回作成したコードは `cursor/ai-702b` ブランチにあります。

```bash
git checkout cursor/ai-702b
```

### 3. 環境構築
必要なライブラリをインストールします。

```bash
cd ai-tele-appointment
pip install -r requirements.txt
```

### 4. 環境変数の設定
VapiのAPIキーを設定するために、`.env.example` をコピーして `.env` を作成し、キーを記入します。

```bash
cp .env.example .env
# .env ファイルを開いて、VAPI_API_KEY にキーを入力してください
```

### 5. サーバーの起動
以下のコマンドでサーバーを立ち上げます。

```bash
python main.py
```

ブラウザで `http://localhost:8000` にアクセスすれば、続きから作業できます。
