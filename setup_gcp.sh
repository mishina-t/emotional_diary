#!/bin/bash

# Google Cloud Natural Language API 設定スクリプト
# このスクリプトを実行してAPIキーを設定してください

echo "🔧 Google Cloud Natural Language API 設定"
echo "=========================================="

# 認証情報ファイルのパスを設定
CREDENTIALS_FILE="credentials.json"

echo ""
echo "📋 設定手順:"
echo "1. Google Cloud Console でサービスアカウントキーをダウンロード"
echo "2. ダウンロードしたJSONファイルを 'credentials.json' としてこのディレクトリに配置"
echo "3. このスクリプトを実行: bash setup_gcp.sh"
echo ""

# 認証情報ファイルの存在確認
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ エラー: $CREDENTIALS_FILE が見つかりません"
    echo ""
    echo "📝 認証情報ファイルの取得方法:"
    echo "1. Google Cloud Console (https://console.cloud.google.com/) にアクセス"
    echo "2. プロジェクトを選択"
    echo "3. 'IAM & Admin' > 'Service Accounts' に移動"
    echo "4. サービスアカウントを作成または選択"
    echo "5. 'Keys' タブ > 'Add Key' > 'Create new key' > 'JSON' を選択"
    echo "6. ダウンロードしたファイルを 'credentials.json' として保存"
    echo ""
    exit 1
fi

# 環境変数を設定
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/$CREDENTIALS_FILE"

echo "✅ 認証情報ファイルが見つかりました: $CREDENTIALS_FILE"
echo "✅ 環境変数を設定しました: GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
echo ""

# API動作確認
echo "🧪 API動作確認中..."
python3 -c "
import os
try:
    from google.cloud import language_v2
    client = language_v2.LanguageServiceClient()
    doc = {'content': '今日はとても楽しい一日でした！', 'type_': language_v2.Document.Type.PLAIN_TEXT, 'language_code': 'ja'}
    resp = client.analyze_sentiment(request={'document': doc})
    print('✅ Google Cloud Natural Language API が正常に動作しています')
    print(f'   感情スコア: {resp.document_sentiment.score:.3f}')
    print(f'   感情の強さ: {resp.document_sentiment.magnitude:.3f}')
except Exception as e:
    print(f'❌ API接続エラー: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 設定完了！"
    echo ""
    echo "📌 使用方法:"
    echo "1. このターミナルセッションでアプリケーションを起動:"
    echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "2. または、新しいターミナルで環境変数を設定してから起動:"
    echo "   export GOOGLE_APPLICATION_CREDENTIALS=\"$(pwd)/$CREDENTIALS_FILE\""
    echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "🌐 ブラウザで http://localhost:8000 にアクセスして日記を書いてみてください！"
else
    echo ""
    echo "❌ 設定に失敗しました。認証情報ファイルを確認してください。"
fi
