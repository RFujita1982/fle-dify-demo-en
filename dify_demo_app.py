"""
自社ブランド RAG デモアプリ
============================
Dify の chat-messages API を裏で叩いて、表は完全に自社ブランドの
チャット画面として見せるための Streamlit アプリ。

顧客には「Dify」という文字は一切見えない。見えるのは下の BRAND で
設定した名前・色・ロゴだけ。

実行方法:
    1) pip install -r requirements.txt
    2) .streamlit/secrets.toml に API キーとエンドポイントを書く
       (.streamlit/secrets.toml.example をコピーして使う)
    3) streamlit run dify_demo_app.py
"""

import json
import uuid

import requests
import streamlit as st

# 自社ロゴ（透過PNGをbase64で同梱。差し替えたいときはここを置換）
LOGO_B64 = "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"

# ============================================================
# ★ここだけ書き換えれば自社ブランドになる★
# ============================================================
BRAND = {
    "name": "FLE Global 合同会社",          # 画面タイトル / タブ名
    "tagline": "製品マニュアルAIサポート",     # サブタイトル
    "engine": "Document AI Engine - α ver.",  # エンジン名・バージョン（タイトル直下）
    "logo_emoji": "✦",                      # ロゴ画像が無いとき用の記号
    "logo_url": "",                          # 画像URLを入れると優先表示 (例 "https://.../logo.png")
    "primary": "#1f3a5f",                    # メインカラー(濃紺)
    "accent": "#c0703a",                     # アクセント(テラコッタ)
    "welcome": "ご質問をどうぞ。製品マニュアルの内容に基づいてお答えします。",
    "input_placeholder": "製品について質問を入力…",
    "show_sources": True,                    # RAGの出典を表示するか(デモの目玉)
    "sources_label": "📄 回答の根拠",
}
# ============================================================


# --- Dify 接続情報は secrets から読む(フロントには絶対書かない) ---
DIFY_BASE = st.secrets.get("dify", {}).get("base_url", "https://api.dify.ai/v1")
DIFY_KEY = st.secrets.get("dify", {}).get("api_key", "")


def upload_file_to_dify(uploaded_file):
    """
    Streamlit の UploadedFile を Dify の /files/upload に送って
    file_id を含む辞書を返す。失敗時は None。
    """
    url = f"{DIFY_BASE}/files/upload"
    headers = {"Authorization": f"Bearer {DIFY_KEY}"}  # multipart なので Content-Type は付けない
    files = {"file": (uploaded_file.name,
                      uploaded_file.getvalue(),
                      uploaded_file.type or "application/octet-stream")}
    data = {"user": st.session_state.user_id}
    try:
        r = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        r.raise_for_status()
        j = r.json()
        # 拡張子からタイプを判定（Dify の type: image / document / audio / video）
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
        image_exts = {"jpg", "jpeg", "png", "gif", "webp", "svg"}
        kind = "image" if ext in image_exts else "document"
        return {
            "type": kind,
            "transfer_method": "local_file",
            "upload_file_id": j.get("id"),
            "name": uploaded_file.name,  # 表示用（payloadには載せない）
        }
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ ファイル送信失敗：{uploaded_file.name}（{e}）")
        return None


def dify_stream(query: str, conversation_id: str, holder: dict, files: list = None):
    """
    Dify にストリーミングで問い合わせるジェネレータ。
    回答テキストの断片を逐次 yield しつつ、conversation_id と
    出典(retriever_resources)は holder 経由で呼び出し側に返す。
    files が渡されていれば payload に同梱する（添付PDF等の参照）。
    """
    url = f"{DIFY_BASE}/chat-messages"
    headers = {
        "Authorization": f"Bearer {DIFY_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "conversation_id": conversation_id or "",   # 空文字なら新規会話
        "user": st.session_state.user_id,
    }
    if files:
        # 表示用の name は Dify に送らない（必要なキーだけ抽出）
        payload["files"] = [
            {k: v for k, v in f.items()
             if k in ("type", "transfer_method", "upload_file_id", "url")}
            for f in files
        ]

    try:
        with requests.post(url, headers=headers, json=payload,
                           stream=True, timeout=120) as resp:
            resp.raise_for_status()
            # Dify は "data: {...}" を \n\n 区切りで流してくる
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data:"):
                    continue
                chunk = raw[5:].strip()      # "data:" の後ろを取り出す
                if not chunk:
                    continue
                try:
                    data = json.loads(chunk)
                except json.JSONDecodeError:
                    continue                 # ping等の非JSON行は無視

                # 会話IDは毎イベントに入るので拾っておく
                if data.get("conversation_id"):
                    holder["conversation_id"] = data["conversation_id"]

                event = data.get("event")
                if event in ("message", "agent_message"):
                    # 回答テキストの断片
                    yield data.get("answer", "")
                elif event == "message_end":
                    # 終了イベント。ここに出典がまとまって入る
                    meta = data.get("metadata", {}) or {}
                    holder["sources"] = meta.get("retriever_resources", []) or []
                elif event == "error":
                    yield f"\n\n⚠️ エラーが発生しました: {data.get('message', '不明')}"
    except requests.exceptions.RequestException as e:
        yield f"\n\n⚠️ 接続エラー: {e}"


def render_sources(sources: list):
    """retriever_resources を「根拠」として折りたたみ表示する。"""
    if not BRAND["show_sources"] or not sources:
        return
    with st.expander(f"{BRAND['sources_label']}（{len(sources)}件）"):
        for s in sources:
            doc = s.get("document_name", "不明な文書")
            score = s.get("score")
            score_txt = f"　関連度 {score:.2f}" if isinstance(score, (int, float)) else ""
            st.markdown(f"**{doc}**{score_txt}")
            content = (s.get("content") or "").strip()
            if content:
                # 長すぎる根拠は冒頭だけ見せる
                preview = content[:300] + ("…" if len(content) > 300 else "")
                st.caption(preview)


def inject_brand_css():
    """自社ブランドの見た目を当てる(Dify色を完全に消す)。"""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Source+Sans+3:wght@400;600&display=swap');

    html, body, .stApp {{
        font-family: 'Source Sans 3', sans-serif;
    }}
    /* アイコン(Material Symbols)はフォントを死守 → 開閉ボタンの文字化け防止 */
    .stApp [data-testid="stIconMaterial"],
    .stApp span[class*="material-symbols"],
    .stApp .material-icons {{
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }}
    .brand-header {{
        display: flex; align-items: center; gap: 14px;
        padding: 4px 0 18px 0;
        border-bottom: 1px solid rgba(0,0,0,0.08);
        margin-bottom: 8px;
    }}
    .brand-logo-img {{ height: 54px; width: auto; flex-shrink: 0; }}
    .brand-title {{
        font-family: 'Fraunces', serif; font-weight: 600;
        font-size: 1.35rem; line-height: 1.15; color: {BRAND['primary']};
        margin: 0;
    }}
    .brand-engine {{
        font-size: 0.82rem; color: {BRAND['accent']}; font-weight: 600;
        letter-spacing: 0.03em; margin: 4px 0 1px 0;
    }}
    .brand-tagline {{ font-size: 0.85rem; color: #6b7280; margin: 2px 0 0 0; }}
    /* 送信ボタンや強調色をブランドのアクセントに */
    .stChatInput textarea:focus {{ border-color: {BRAND['accent']} !important; }}
    [data-testid="stChatMessageAvatarUser"] {{ background: {BRAND['accent']} !important; }}
    [data-testid="stChatMessageAvatarAssistant"] {{ background: {BRAND['primary']} !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header():
    st.markdown(
        f"""
        <div class="brand-header">
            <div>
                <p class="brand-engine">{BRAND['engine']}</p>
                <p class="brand-tagline">{BRAND['tagline']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 画面本体
# ============================================================
st.set_page_config(page_title=BRAND["name"], page_icon=BRAND["logo_emoji"])
inject_brand_css()
render_header()

# --- 状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""
if "user_id" not in st.session_state:
    # 顧客ごとに一意のID(デモ中の会話を区別するため)
    st.session_state.user_id = f"demo-{uuid.uuid4().hex[:8]}"

# APIキー未設定の警告(デモ前のセルフチェック用)
if not DIFY_KEY:
    st.warning("接続キーが未設定です。.streamlit/secrets.toml を確認してください。")

# 「会話をリセット」ボタン
with st.sidebar:
    st.markdown(
        f'<img src="data:image/png;base64,{LOGO_B64}" '
        f'style="height:96px;width:auto;display:block;margin:4px 0 10px 0;">',
        unsafe_allow_html=True,
    )
    st.markdown(f"### {BRAND['name']}")
    if st.button("会話をリセット", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = ""
        st.rerun()

# ウェルカム表示(まだ会話が無いとき)
if not st.session_state.messages:
    st.info(BRAND["welcome"])

# これまでの履歴を再描画
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"])
        for fname in msg.get("files", []):
            st.markdown(f"📎 *{fname}*")
        if msg["role"] == "assistant":
            render_sources(msg.get("sources", []))

# --- 入力欄（テキスト＋ファイル添付対応）---
prompt_value = st.chat_input(
    BRAND["input_placeholder"],
    accept_file="multiple",
    file_type=["pdf", "txt", "md", "csv", "html",
               "docx", "xlsx", "pptx",
               "jpg", "jpeg", "png"],
)
if prompt_value:
    user_text = (prompt_value.text or "").strip()
    user_files = prompt_value.files or []

    # 添付があれば先に Dify にアップロード
    file_refs = []
    if user_files:
        with st.spinner(f"📎 添付ファイルを送信中…（{len(user_files)}件）"):
            for f in user_files:
                ref = upload_file_to_dify(f)
                if ref:
                    file_refs.append(ref)

    # テキストも添付も両方ゼロなら何もしない
    if user_text or file_refs:
        # ユーザー発言を表示・記録（添付名も保存して履歴再描画に対応）
        st.session_state.messages.append({
            "role": "user",
            "content": user_text,
            "files": [r["name"] for r in file_refs],
        })
        with st.chat_message("user"):
            if user_text:
                st.markdown(user_text)
            for ref in file_refs:
                st.markdown(f"📎 *{ref['name']}*")

        # 本文が空の場合の保険（ファイルだけ送られたとき）
        query_for_api = user_text or "添付ファイルの内容を確認し、要点を整理してください。"

        # アシスタント応答(ストリーミング、添付付き)
        with st.chat_message("assistant"):
            holder = {"conversation_id": st.session_state.conversation_id, "sources": []}
            answer = st.write_stream(
                dify_stream(query_for_api,
                            st.session_state.conversation_id,
                            holder,
                            files=file_refs)
            )
            st.session_state.conversation_id = holder["conversation_id"]
            render_sources(holder["sources"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": holder["sources"],
        })
