import streamlit as st
from dotenv import load_dotenv
from auth import auth_required
import time

load_dotenv()

st.set_page_config(
    page_title="LangGraph Demo",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.session_state.step = "idle"  # idle, init, summarize, review, title, done
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

@auth_required
def render_main_ui():
    st.markdown("""
    <div style="margin: 20px 0 30px 0; padding: 20px 0 15px 0; border-bottom: 2px solid #00796B;">
        <img src="https://langchain-ai.github.io/langgraph/static/wordmark_dark.svg" 
             alt="LangGraph" 
             style="width: 300px; display: block; max-width: 100%;">
    </div>
    """, unsafe_allow_html=True)
    
    # プレースホルダー
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
    
    # 現在の状態とノードを取得
    current_state = {
        "revision_count": st.session_state.state.get("revision_count", 0),
        "approved": st.session_state.state.get("approved", False),
        "dialog_history": st.session_state.dialog_history
    }
    
    # ワークフロー可視化（空のコンテナを作成）
    workflow_viz_container = st.empty()
    with workflow_viz_container:
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
    run_button = st.button(
        "実行", 
        key="run_button", 
        use_container_width=True,
        disabled=st.session_state.step != "idle" and st.session_state.step != "done"
    )
    
    # エージェント対話履歴セクション
    st.subheader("エージェント対話履歴")
    
    # 進捗状況表示用コンテナ（空のコンテナとして作成）
    progress_status_container = st.empty()
    
    # 対話履歴表示用コンテナ（空のコンテナとして作成）
    dialog_container = st.empty()
    
    # 実行ボタンが押された場合の処理
    if run_button:
        if not user_input:
            st.error("文章が入力されていません。")
        else:
            # 状態をリセット
            st.session_state.step = "running"
            st.session_state.error = None
            st.session_state.progress = 0
            st.session_state.dialog_history = []
            
            try:
                # 初期状態の作成
                state = create_initial_state(user_input)
                st.session_state.state = state
                
                # プログレスバーを表示
                with progress_status_container:
                    st.progress(0)
                    st.markdown("""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを初期化しています
                        </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # 完了メッセージ
                state = add_to_dialog_history(
                    state, 
                    "system", 
                    "すべての処理が完了しました。",
                    progress=100
                )
                
                st.session_state.current_node = "END"
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 100
                
                # ワークフロー可視化を更新
                with workflow_viz_container:
                    render_workflow_visualization(
                        {
                            "revision_count": state.get("revision_count", 0),
                            "approved": state.get("approved", False),
                            "dialog_history": st.session_state.dialog_history
                        }, 
                        "END"
                    )
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(100/100)
                    
                # 最終結果の表示
                with st.session_state.result_placeholder:
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
                
                # 処理完了
                st.session_state.step = "done"
                
            except Exception as e:
                # エラーハンドリング
                st.session_state.error = str(e)
                st.session_state.step = "done"
                st.error(f"エラーが発生しました: {str(e)}")
    
    # 対話履歴の表示（初期状態の場合）
    if st.session_state.step == "idle":
        with dialog_container:
            st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    render_sidebar()
    render_main_ui()>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 初期化メッセージ
                state = add_to_dialog_history(
                    state,
                    "system",
                    "新しいテキストが入力されました。ワークフローを開始します。",
                    progress=5
                )
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 5
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(5/100)
                    st.markdown("""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを初期化しています
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # ---------- 要約ステップ ----------
                st.session_state.current_node = "summarize"
                st.session_state.current_description = get_node_description("summarize")
                
                # ワークフロー可視化を更新
                with workflow_viz_container:
                    render_workflow_visualization(
                        {
                            "revision_count": state.get("revision_count", 0),
                            "approved": state.get("approved", False),
                            "dialog_history": st.session_state.dialog_history
                        }, 
                        "summarize"
                    )
                
                # 要約作成
                state["revision_count"] += 1
                
                # 対話履歴に追加
                state = add_to_dialog_history(
                    state, 
                    "system", 
                    f"要約エージェントが要約を作成 (第{state['revision_count']}版)",
                    progress=10
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 10
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(10/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # 要約生成中メッセージ
                state = add_to_dialog_history(
                    state, 
                    "summarizer", 
                    "要約を生成しています...",
                    progress=20
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 20
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(20/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # 分析中メッセージ
                state = add_to_dialog_history(
                    state, 
                    "summarizer", 
                    "テキストを分析中...",
                    progress=30
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 30
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(30/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # 要約前メッセージ
                if state["revision_count"] == 1:
                    action_msg = "初回の要約を作成中..."
                else:
                    action_msg = "フィードバックを基に要約を改善中..."
                    
                state = add_to_dialog_history(
                    state, 
                    "summarizer", 
                    action_msg,
                    progress=40
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 40
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(40/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 実際の要約生成（API呼び出し）
                client = get_client()
                agent = SummarizerAgent(client)
                
                if state["revision_count"] == 1:
                    summary = agent.call(state["input_text"])
                else:
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
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 60
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(60/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # ---------- レビューステップ ----------
                st.session_state.current_node = "review"
                st.session_state.current_description = get_node_description("review")
                
                # ワークフロー可視化を更新
                with workflow_viz_container:
                    render_workflow_visualization(
                        {
                            "revision_count": state.get("revision_count", 0),
                            "approved": state.get("approved", False),
                            "dialog_history": st.session_state.dialog_history
                        }, 
                        "review"
                    )
                
                # 対話履歴に追加
                state = add_to_dialog_history(
                    state, 
                    "system", 
                    "批評エージェントが要約レビューを実施",
                    progress=65
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 65
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(65/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # レビュー実施中メッセージ
                state = add_to_dialog_history(
                    state, 
                    "reviewer", 
                    "レビューを実施しています...",
                    progress=70
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 70
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(70/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # 評価中メッセージ
                state = add_to_dialog_history(
                    state, 
                    "reviewer", 
                    "要約の品質を評価中...",
                    progress=75
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 75
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(75/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # レビュー実行
                agent = ReviewerAgent(client)
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
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 80
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(80/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
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
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 85
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(85/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # 承認されていない場合は要約ステップに戻る
                if not is_approved and state["revision_count"] < 3:
                    # 再度要約ステップを実行するコードをここに追加
                    # このサンプルでは省略（繰り返しを避けるため）
                    pass
                
                # ---------- タイトル生成ステップ ----------
                st.session_state.current_node = "title_node"
                st.session_state.current_description = get_node_description("title_node")
                
                # ワークフロー可視化を更新
                with workflow_viz_container:
                    render_workflow_visualization(
                        {
                            "revision_count": state.get("revision_count", 0),
                            "approved": state.get("approved", False),
                            "dialog_history": st.session_state.dialog_history
                        }, 
                        "title_node"
                    )
                
                # 対話履歴に追加
                state = add_to_dialog_history(
                    state, 
                    "system", 
                    "タイトル命名エージェントがタイトルを生成します",
                    progress=87
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 87
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(87/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # タイトル生成メッセージ
                state = add_to_dialog_history(
                    state, 
                    "title", 
                    "タイトルを生成しています...",
                    progress=90
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 90
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(90/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                time.sleep(0.5)  # UIの更新を確認するための短い待機
                
                # 検討中メッセージ
                state = add_to_dialog_history(
                    state, 
                    "title", 
                    "要約内容からタイトルを検討中...",
                    progress=93
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 93
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(93/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # タイトル生成
                agent = TitleCopywriterAgent(client)
                output = agent.call(state["input_text"], state.get("transcript", []), state["summary"])
                
                state["title"] = output.get("title", "")
                state["final_summary"] = output.get("summary", "")
                
                # 対話履歴に追加
                state = add_to_dialog_history(
                    state,
                    "title",
                    f"【生成タイトル】『{state['title']}』",
                    progress=96
                )
                
                st.session_state.state = state
                st.session_state.dialog_history = state["dialog_history"]
                st.session_state.progress = 96
                
                # 対話履歴を更新
                with dialog_container:
                    display_dialog_history(st.session_state.dialog_history)
                
                # プログレスバーを更新
                with progress_status_container:
                    st.progress(96/100)
                    st.markdown(f"""
                    <div class="processing-indicator">
                        <div class="processing-icon">⚙️</div>
                        <div>
                            <strong>処理中...</strong> ワークフローを実行しています
                            <div class="latest-action">{st.session_state.current_description}</div>
                        </div>
                    </div
