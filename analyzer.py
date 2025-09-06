import os, json, math

def _emoji_valence(emojis: str) -> float:
    if not emojis: return 0.0
    table = {"😊":0.7,"😄":0.8,"😁":0.9,"😆":0.8,"🙂":0.4,
             "😢":-0.7,"😞":-0.6,"😡":-0.8,"😐":0.0,"😴":-0.2}
    vals = [table.get(e.strip(), 0.0) for e in emojis.split(",") if e.strip()]
    return sum(vals)/len(vals) if vals else 0.0

def _word_valence(text: str) -> float:
    pos = ["楽しい","嬉しい","最高","ワクワク","よかった","快適"]
    neg = ["疲れた","しんどい","最悪","むかつく","だるい","不安"]
    score = 0
    for w in pos:
        if w in text: score += 1
    for w in neg:
        if w in text: score -= 1
    return max(min(score/5.0, 1.0), -1.0)

def _mood_norm(mood: int) -> float:
    mood = max(1, min(5, mood))
    return (mood - 3) / 2.0  # 1→-1, 5→+1

def _combine(text_val, emoji_val, mood_val):
    s = 0.5*text_val + 0.3*emoji_val + 0.2*mood_val
    return max(min(s, 1.0), -1.0)

def analyze_text(text: str, emojis: str, mood: int):
    # 1) まずGoogle NL API（環境変数が設定されている場合のみ）
    cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    try:
        if cred and os.path.exists(cred):
            from google.cloud import language_v2
            client = language_v2.LanguageServiceClient()
            doc = {"content": text, "type_": language_v2.Document.Type.PLAIN_TEXT, "language_code": "ja"}
            resp = client.analyze_sentiment(request={"document": doc})
            score = float(resp.document_sentiment.score)  # -1.0〜1.0
            magnitude = float(resp.document_sentiment.magnitude)
            # 絵文字＆moodで微調整
            score = _combine(score, _emoji_valence(emojis), _mood_norm(mood))
            return {"score": score, "magnitude": magnitude}
    except Exception:
        pass

    # 2) フォールバック（ローカル辞書）
    t = _word_valence(text)
    e = _emoji_valence(emojis)
    m = _mood_norm(mood)
    return {"score": _combine(t, e, m), "magnitude": abs(t) + abs(e)}