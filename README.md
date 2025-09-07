# 📝 Emotional Diary

Google Cloud Natural Language APIを使用した高精度な感情分析機能を持つ日記アプリケーションです。

## 🚀 機能

- **高精度な感情分析**: Google Cloud Natural Language APIによる感情スコア計算
- **絵文字感情分析**: 絵文字から感情を読み取り
- **気分記録**: 1-5段階での気分評価
- **データ可視化**: 気分と感情スコアのグラフ表示
- **レスポンシブデザイン**: モバイル対応の美しいUI

## 📋 必要な環境

- Python 3.8以上
- Google Cloud Platform アカウント
- Google Cloud Natural Language API の有効化

## 🛠️ セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Natural Language API の設定

#### 2.1 Google Cloud Console での設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. **API とサービス** > **ライブラリ** に移動
4. "Natural Language API" を検索して有効化
5. **IAM & Admin** > **サービス アカウント** に移動
6. サービスアカウントを作成または選択
7. **キー** タブ > **キーを追加** > **新しいキーを作成** > **JSON** を選択
8. ダウンロードしたJSONファイルを `credentials.json` としてプロジェクトディレクトリに保存

#### 2.2 認証情報の設定

```bash
# 設定スクリプトを実行
bash setup_gcp.sh
```

または手動で環境変数を設定：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### 3. API動作確認

```bash
python test_api.py
```

### 4. アプリケーションの起動

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

ブラウザで `http://localhost:8000` にアクセス

## 📁 プロジェクト構造

```
emotional_diary/
├── main.py                 # FastAPIアプリケーション
├── analyzer.py             # 感情分析モジュール
├── app.db                  # SQLiteデータベース
├── requirements.txt        # 依存関係
├── setup_gcp.sh           # Google Cloud設定スクリプト
├── test_api.py            # API動作確認スクリプト
├── credentials.json        # Google Cloud認証情報（要設定）
├── templates/             # HTMLテンプレート
│   ├── home.html          # ホームページ
│   └── entry.html         # 日記作成フォーム
└── static/                # 静的ファイル（現在未使用）
```

## 🔧 使用方法

### 日記の作成

1. **日付**: 日記の日付を選択
2. **テキスト**: 今日の出来事や気持ちを記入
3. **絵文字**: 気分を表す絵文字を選択（複数選択可）
4. **気分**: 1-5段階で全体的な気分を評価
5. **保存**: 日記を保存して感情分析を実行

### データの表示

- **気分の変化**: 最近30日間の気分（1-5）のグラフ
- **感情スコア**: 感情分析結果（-1〜1）のグラフ
- **提案**: 最近の感情スコアに基づくアドバイス

## 🧠 感情分析の仕組み

### Google Cloud Natural Language API使用時

1. **テキスト分析**: Googleの機械学習モデルで感情スコアを計算
2. **絵文字補正**: 絵文字の感情価値を加算
3. **気分補正**: ユーザー入力の気分で微調整
4. **最終スコア**: 3つの要素を重み付けして統合

### ローカル分析（フォールバック）

- Google Cloud APIが利用できない場合の簡易分析
- 事前定義された感情語彙を使用
- 絵文字と気分の組み合わせで感情スコアを計算

## 🔒 セキュリティ

- 認証情報ファイル（`credentials.json`）は機密情報です
- このファイルをバージョン管理に含めないでください
- `.gitignore` に `credentials.json` を追加することを推奨

## 🐛 トラブルシューティング

### API接続エラー

```bash
# 認証情報の確認
echo $GOOGLE_APPLICATION_CREDENTIALS

# ファイルの存在確認
ls -la credentials.json

# API動作確認
python test_api.py
```

### 依存関係エラー

```bash
# 依存関係の再インストール
pip install -r requirements.txt --force-reinstall
```

## 📊 データベース

SQLiteデータベース（`app.db`）に以下の情報が保存されます：

- **id**: エントリの一意ID
- **date**: 日付
- **text**: 日記のテキスト
- **emojis**: 選択された絵文字
- **mood**: 気分評価（1-5）
- **sentiment_score**: 感情スコア（-1〜1）
- **sentiment_magnitude**: 感情の強さ
- **created_at**: 作成日時

## 🎯 今後の拡張予定

- [ ] 感情の詳細分析（喜び、悲しみ、怒りなど）
- [ ] データのエクスポート機能
- [ ] 感情の傾向分析
- [ ] カスタム感情語彙の追加
- [ ] 複数ユーザー対応

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します！

---

**注意**: Google Cloud Natural Language APIの使用には料金が発生する場合があります。詳細は[Google Cloud料金ページ](https://cloud.google.com/natural-language/pricing)をご確認ください。
