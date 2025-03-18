import streamlit as st
import time
import threading
from dotenv import load_dotenv
from auth import auth_required

load_dotenv()

st.set_page_config(
    page_title="LangGraph Demo",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSSスタイルは省略（元のコードを使用）

from components.sidebar import render_sidebar
from components.workflow_viz import render_workflow_visualization
from components.dialog_history import display_dialog_history, add_to_dialog_history

from utils.api_client import initialize_client, get_client
initialize_client()

from agents.summarizer import SummarizerAgent
from agents.reviewer import ReviewerAgent
from agents.title_writer import TitleCopywriterAgent
from utils.state import create_initial_state

# シンプルな状態管理
if 'step' not in st.session_state:
    st.session_state.step = "idle"  # idle, init, running, done
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'state' not in st.session_state:
    st.session_state.state = {}
if 'dialog_history' not in st.session_state:
    st.session_state.dialog_history = []
if 'error' not in st.session_state:
    st.session_state.error = None
if 'current_node' not in st.session_state:
    st.session_state.current_node = ""
if 'current_description' not in st.session_state:
    st.session_state.current_description = ""
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
if 'process_thread' not in st.session_state:
    st.session_state.process_thread = None
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = time.time()

def get_node_description(node_name):
    """ノード名に基づいて説明テキストを取得"""
    descriptions = {
        "summarize": "テキストの要約を生成しています...",
        "review": "要約の品質を評価しています...",
        "title_node": "適切なタイトルを付与しています...",
        "END": "処理が完了しました！",
        "": "ワークフローを初期化中..."
    }
    return descriptions.get(node_name, "処理中...")

def process_step_thread():
    """バックグラウンドスレッドで現在のステップに基づいて処理を実行"""
    try:
        # 初期化ステップ
        if st.session_state.step == "init":
            user_input = st.session_state.input_text
            
            # 初期状態作成
            state = create_initial_state(user_input)
            state = add_to_dialog_history(
                state,
                "system",
                "新しいテキストが入力されました。ワークフローを開始します。",
                progress=5
            )
            
            # 状態更新（排他制御なしでも大丈夫な変数）
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.progress = 5
            st.session_state.current_node = ""
            st.session_state.current_description = "ワークフローを初期化中..."
            st.session_state.last_update_time = time.time()
            
            # 次のステップへ
            st.session_state.step = "summarize"
            
        # 要約ステップ
        elif st.session_state.step == "summarize":
            st.session_state.current_node = "summarize"
            st.session_state.current_description = get_node_description("summarize")
            st.session_state.progress = 30
            st.session_state.last_update_time = time.time()
            
            state = st.session_state.state
            client = get_client()
            agent = SummarizerAgent(client)
            
            # 要約作成
            state["revision_count"] += 1
            
            # 対話履歴に追加
            state = add_to_dialog_history(
                state, 
                "system", 
                f"要約エージェントが要約を作成 (第{state['revision_count']}版)",
                progress=10
            )
            
            # 状態更新
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 中間ステップのログを追加
            state = add_to_dialog_history(
                state, 
                "summarizer", 
                "要約を生成しています...",
                progress=20
            )
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.progress = 20
            st.session_state.last_update_time = time.time()
            
            # さらに中間ステップ
            state = add_to_dialog_history(
                state, 
                "summarizer", 
                "テキストを分析中...",
                progress=30
            )
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.progress = 30
            st.session_state.last_update_time = time.time()
            
            # 要約生成
            if state["revision_count"] == 1:
                state = add_to_dialog_history(
                    state, 
                    "summarizer", 
                    "初回の要約を作成中...",
                    progress=40
                )
                
                st.session_state.progress = 40
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.last_update_time = time.time()
                
                summary = agent.call(state["input_text"])
            else:
                state = add_to_dialog_history(
                    state, 
                    "summarizer", 
                    "フィードバックを基に要約を改善中...",
                    progress=40
                )
                
                st.session_state.progress = 40
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.last_update_time = time.time()
                
                summary = agent.refine(state["input_text"], state["feedback"])
            
            # 状態更新
            state["summary"] = summary
            
            # 対話履歴に追加
            state = add_to_dialog_history(
                state, 
                "summarizer", 
                f"【要約 第{state['revision_count']}版】\n{summary}",
                progress=60
            )
            
            st.session_state.progress = 60
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 次のステップへ
            st.session_state.step = "review"
            
        # レビューステップ
        elif st.session_state.step == "review":
            st.session_state.current_node = "review"
            st.session_state.current_description = get_node_description("review")
            st.session_state.progress = 65
            st.session_state.last_update_time = time.time()
            
            state = st.session_state.state
            client = get_client()
            agent = ReviewerAgent(client)
            
            # 対話履歴に追加
            state = add_to_dialog_history(
                state, 
                "system", 
                "批評エージェントが要約レビューを実施",
                progress=65
            )
            
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 中間ステップのログ
            state = add_to_dialog_history(
                state, 
                "reviewer", 
                "レビューを実施しています...",
                progress=70
            )
            
            st.session_state.progress = 70
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 評価中メッセージ
            state = add_to_dialog_history(
                state, 
                "reviewer", 
                "要約の品質を評価中...",
                progress=75
            )
            
            st.session_state.progress = 75
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # レビュー実行
            is_final_review = (state["revision_count"] >= 3)
            
            feedback = agent.call(
                current_summary=state["summary"],
                previous_summary=state.get("previous_summary", ""),
                previous_feedback=state.get("previous_feedback", ""),
                is_final_review=is_final_review
            )
            
            # 状態更新
            state["feedback"] = feedback
            state["previous_summary"] = state["summary"]
            state["previous_feedback"] = feedback
            
            # 対話履歴に追加
            state = add_to_dialog_history(
                state,
                "reviewer",
                f"【フィードバック】\n{feedback}",
                progress=80
            )
            
            st.session_state.progress = 80
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 承認判定
            is_approved = agent.check_approval(feedback, state["revision_count"])
            state["approved"] = is_approved
            
            # 判定結果をログ
            judge_msg = "承認" if is_approved else "改訂が必要"
            state = add_to_dialog_history(
                state,
                "reviewer",
                f"【判定】{judge_msg}",
                progress=85
            )
            
            st.session_state.progress = 85
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 次のステップを判断
            if is_approved or state["revision_count"] >= 3:
                st.session_state.step = "title"
            else:
                st.session_state.step = "summarize"
            
        # タイトル生成ステップ
        elif st.session_state.step == "title":
            st.session_state.current_node = "title_node"
            st.session_state.current_description = get_node_description("title_node")
            st.session_state.progress = 87
            st.session_state.last_update_time = time.time()
            
            state = st.session_state.state
            client = get_client()
            agent = TitleCopywriterAgent(client)
            
            # 対話履歴に追加
            state = add_to_dialog_history(
                state, 
                "system", 
                "タイトル命名エージェントがタイトルを生成します",
                progress=87
            )
            
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 中間ステップのログ
            state = add_to_dialog_history(
                state, 
                "title", 
                "タイトルを生成しています...",
                progress=90
            )
            
            st.session_state.progress = 90
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 検討中メッセージ
            state = add_to_dialog_history(
                state, 
                "title", 
                "要約内容からタイトルを検討中...",
                progress=93
            )
            
            st.session_state.progress = 93
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # タイトル生成
            output = agent.call(state["input_text"], state.get("transcript", []), state["summary"])
            
            # 状態更新
            state["title"] = output.get("title", "")
            state["final_summary"] = output.get("summary", "")
            
            # 対話履歴に追加
            state = add_to_dialog_history(
                state,
                "title",
                f"【生成タイトル】『{state['title']}』",
                progress=96
            )
            
            st.session_state.progress = 96
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 完了メッセージ
            state = add_to_dialog_history(
                state, 
                "system", 
                "すべての処理が完了しました。",
                progress=100
            )
            
            st.session_state.progress = 100
            st.session_state.current_node = "END"
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.last_update_time = time.time()
            
            # 完了
            st.session_state.step = "done"
            
    except Exception as e:
        st.session_state.error = str(e)
        st.session_state.step = "done"  # エラー時も処理を終了
    
    # 処理完了フラグを設定
    st.session_state.processing_done = True

def start_processing():
    """バックグラウンドスレッドで処理を開始"""
    if st.session_state.process_thread is None or not st.session_state.process_thread.is_alive():
        st.session_state.processing_done = False
        st.session_state.process_thread = threading.Thread(target=process_step_thread)
        st.session_state.process_thread.daemon = True
        st.session_state.process_thread.start()

@auth_required
def render_main_ui():
    # プレースホルダー
    st.markdown("""
    <div style="margin: 20px 0 30px 0; padding: 20px 0 15px 0; border-bottom: 2px solid #00796B;">
        <img src="https://langchain-ai.github.io/langgraph/static/wordmark_dark.svg" 
             alt="LangGraph" 
             style="width: 300px; display: block; max-width: 100%;">
    </div>
    """, unsafe_allow_html=True)
    
    if 'result_placeholder' not in st.session_state:
        st.session_state.result_placeholder = st.empty()

    # メイン画面
    st.markdown("""
    <div class="card">
        <p>
            テキスト要約を行う3つのエージェント（要約者、批評家、タイトル作成者）が協力して作業します。
            入力したテキストを要約し、批評・改善を経て、最終的に適切なタイトルがつけられます。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ワークフロー可視化
    # 現在の状態とノードを取得
    current_state = {
        "revision_count": st.session_state.state.get("revision_count", 0),
        "approved": st.session_state.state.get("approved", False),
        "dialog_history": st.session_state.dialog_history
    }
    
    render_workflow_visualization(current_state, st.session_state.current_node)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # サンプルテキストの定義
    example_texts = [
        "例文を選択してください...",
        "人工知能（AI）は、機械学習、深層学習、自然言語処理などの技術を通じて、人間のような知能を模倣するコンピュータシステムです。近年のAI技術の急速な進歩により、自動運転車、医療診断、翻訳サービスなど、様々な分野で革新的なアプリケーションが開発されています。",
        "宇宙探査は人類の好奇心と技術の集大成です。太陽系の惑星や衛星への無人探査機の送付から、国際宇宙ステーションでの有人ミッション、さらには将来の火星有人探査計画まで、私たちは宇宙への理解を深め続けています。"
    ]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("テキスト入力")
    with col2:
        selected_example = st.selectbox(
            "サンプルを選択", 
            example_texts,
            key="example_selector",
            label_visibility="collapsed"
        )
    default_text = selected_example if selected_example != example_texts[0] else ""
    user_input = st.text_area(
        "要約したい文章を入力してください", 
        value=default_text,
        height=150, 
        key="input_text",
        label_visibility="collapsed"
    )
    
    # 実行ボタン（処理中は無効化）
    is_processing = st.session_state.step not in ["idle", "done"]
    run_button = st.button(
        "実行", 
        key="run_button", 
        use_container_width=True,
        disabled=is_processing
    )
    
    # エージェント対話履歴セクション
    st.subheader("エージェント対話履歴")
    
    # 進捗状況表示用コンテナ
    progress_status_container = st.container()
    dialog_container = st.container()
    
    # 実行ボタンが押された場合の処理
    if run_button:
        if not user_input:
            st.error("文章が入力されていません。")
        else:
            # 実行開始
            st.session_state.step = "init"
            st.session_state.error = None
            st.session_state.processing_done = False
            
            # バックグラウンド処理を開始
            start_processing()
    
    # 処理中・完了後の表示
    with progress_status_container:
        if st.session_state.step != "idle":
            # プログレスバー
            st.progress(st.session_state.progress / 100)
            
            # 処理中表示
            if st.session_state.step != "done":
                st.markdown(f"""
                <div class="processing-indicator">
                    <div class="processing-icon">⚙️</div>
                    <div>
                        <strong>処理中...</strong> ワークフローを実行しています
                        <div class="latest-action">{st.session_state.current_description}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 対話履歴の表示
    with dialog_container:
        if st.session_state.dialog_history:
            display_dialog_history(st.session_state.dialog_history)
        else:
            st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
    
    # 最終結果の表示（処理完了後）
    if st.session_state.step == "done" and 'result_placeholder' in st.session_state:
        with st.session_state.result_placeholder:
            state = st.session_state.state
            if "title" in state and "final_summary" in state:
                st.markdown(f"""
                <div class="result-card">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="background-color: #00796B; color: white; width: 32px; height: 32px; 
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                    margin-right: 10px;">✓</div>
                        <span style="color: #00796B; font-weight: bold;">処理が完了しました (100%)</span>
                    </div>
                    <h2>{state['title']}</h2>
                    <div style="padding: 1rem; background-color: #f9f9f9; border-radius: 6px; margin-top: 1rem;">
                        {state["final_summary"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.error:
        st.error(f"エラーが発生しました: {st.session_state.error}")
    
    # 処理中の場合は定期的に更新
    if is_processing and not st.session_state.processing_done:
        # 最後の更新から0.5秒以上経過していたら自動更新
        if time.time() - st.session_state.last_update_time > 0.5:
            time.sleep(0.5)  # 少し待機して状態の更新を待つ
            st.rerun()


if __name__ == "__main__":
    render_sidebar()
    render_main_ui()
