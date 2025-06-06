# BodyScale 起動方法

## 📍 実行場所

### Windows (コマンドプロンプト または PowerShell)

1. **Windowsキー + R** を押して「ファイル名を指定して実行」を開く
2. `cmd` と入力してEnterキー（コマンドプロンプトが開きます）

3. MuscleFormAnalyzerフォルダに移動：
```cmd
cd C:\Users\Owner\MuscleFormAnalyzer
```

4. バッチファイルを実行：
```cmd
start_bodyscale.bat
```

### または、エクスプローラーから直接実行

1. **エクスプローラー**を開く
2. 以下のパスに移動：
   ```
   C:\Users\Owner\MuscleFormAnalyzer
   ```
3. `start_bodyscale.bat` をダブルクリック

## 🚀 実行すると何が起きるか

1. **自動セットアップ** (初回のみ)
   - Python仮想環境の作成
   - 必要なパッケージのインストール
   - 設定ファイルの作成

2. **サーバー起動**
   - バックエンドサーバー (Flask) が起動
   - フロントエンドサーバー (Next.js) が起動

3. **ブラウザが自動で開く**
   - http://localhost:3000 が開きます
   - 開かない場合は手動でこのURLにアクセス

## 📝 注意事項

- 初回実行時は依存関係のインストールで5-10分かかることがあります
- 黒いウィンドウ（コマンドプロンプト）が2つ開きますが、これは正常です
- サーバーを停止するには、各ウィンドウで **Ctrl+C** を押してください

## ❓ エラーが出た場合

### "Python is not installed" エラー
→ Python 3.8以上をインストール: https://python.org

### "Node.js is not installed" エラー
→ Node.js 16以上をインストール: https://nodejs.org

### その他のエラー
→ 管理者権限でコマンドプロンプトを開いて再実行してみてください