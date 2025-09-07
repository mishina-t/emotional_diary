#!/usr/bin/env python3
"""
Google Cloud Natural Language API 動作確認スクリプト
このスクリプトでAPIが正常に動作するかを確認できます
"""

import os
import sys
from analyzer import analyze_text

def test_api_connection():
    """Google Cloud Natural Language APIの接続テスト"""
    print("🔧 Google Cloud Natural Language API 動作確認")
    print("=" * 50)
    
    # 環境変数の確認
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS 環境変数が設定されていません")
        print("   setup_gcp.sh を実行して設定してください")
        return False
    
    if not os.path.exists(cred_path):
        print(f"❌ 認証情報ファイルが見つかりません: {cred_path}")
        return False
    
    print(f"✅ 認証情報ファイル: {cred_path}")
    
    # Google Cloud Language APIの直接テスト
    try:
        from google.cloud import language_v2
        client = language_v2.LanguageServiceClient()
        
        # テスト用の文書
        test_text = "今日はとても楽しい一日でした！"
        doc = {
            "content": test_text,
            "type_": language_v2.Document.Type.PLAIN_TEXT,
            "language_code": "ja"
        }
        
        print(f"📝 テスト文書: {test_text}")
        resp = client.analyze_sentiment(request={"document": doc})
        
        print("✅ Google Cloud Natural Language API が正常に動作しています")
        print(f"   感情スコア: {resp.document_sentiment.score:.3f}")
        print(f"   感情の強さ: {resp.document_sentiment.magnitude:.3f}")
        
    except Exception as e:
        print(f"❌ Google Cloud API エラー: {e}")
        return False
    
    return True

def test_analyzer_function():
    """analyzer.pyのanalyze_text関数のテスト"""
    print("\n🧪 analyzer.py の動作確認")
    print("=" * 30)
    
    # テストケース
    test_cases = [
        {
            "text": "今日は最高の一日でした！",
            "emojis": "😊,😄",
            "mood": 5,
            "description": "ポジティブな感情"
        },
        {
            "text": "疲れたし、最悪の一日だった",
            "emojis": "😢,😞",
            "mood": 1,
            "description": "ネガティブな感情"
        },
        {
            "text": "普通の一日でした",
            "emojis": "😐",
            "mood": 3,
            "description": "中性的な感情"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nテストケース {i}: {case['description']}")
        print(f"  テキスト: {case['text']}")
        print(f"  絵文字: {case['emojis']}")
        print(f"  気分: {case['mood']}/5")
        
        try:
            result = analyze_text(
                text=case['text'],
                emojis=case['emojis'],
                mood=case['mood']
            )
            
            print(f"  ✅ 結果:")
            print(f"     感情スコア: {result['score']:.3f}")
            print(f"     感情の強さ: {result['magnitude']:.3f}")
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")

def main():
    """メイン関数"""
    print("🚀 感情日記アプリ - API動作確認")
    print("=" * 40)
    
    # API接続テスト
    if test_api_connection():
        print("\n🎉 Google Cloud Natural Language API が利用可能です！")
        print("   高精度な感情分析が使用されます。")
    else:
        print("\n⚠️  Google Cloud Natural Language API が利用できません。")
        print("   ローカル分析が使用されます。")
    
    # analyzer関数のテスト
    test_analyzer_function()
    
    print("\n" + "=" * 40)
    print("✅ 動作確認完了")
    print("\n📌 次のステップ:")
    print("1. uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("2. ブラウザで http://localhost:8000 にアクセス")
    print("3. 日記を書いて感情分析を試してみてください！")

if __name__ == "__main__":
    main()
