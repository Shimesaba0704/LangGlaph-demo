import streamlit as st
import time
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
if 'step_progress' not in st.session_state:
    st.session_state.step_progress = 0

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

def update_ui_and_wait(seconds=0.1):
    """UIを更新して少し待機する"""
    st.rerun()
    time.sleep(seconds)  # 非同期処理の場合は必要に応じて調整

def process_init_step():
    """初期化ステップを処理"""
    user_input = st.session_state.input_text
    
    # 初期状態作成
    state = create_initial_state(user_input)
    state = add_to_dialog_history(
        state,
        "system",
        "新しいテキストが入力されました。ワークフローを開始します。",
        progress=5
    )
    
    # 状態更新
    st.session_state.state = state
    st.session_state.dialog_history = state["dialog_history"]
    st.session_state.progress = 5
    st.session_state.current_node = ""
    st.session_state.current_description = "ワークフローを初期化中..."
    st.session_state.step_progress = 0
    
    # UIを更新
    update_ui_and_wait()
    
    # 次のステップへ
    st.session_state.step = "summarize"

def process_summarize_step():
    """要約ステップを処理"""
    # ステップ進捗管理
    if 'step_progress' not in st.session_state:
        st.session_state.step_progress = 0
    
    state = st.session_state.state
    client = get_client()
    agent = SummarizerAgent(client)
    
    # ステップに基づいた処理
    if st.session_state.step_progress == 0:
        st.session_state.current_node = "summarize"
        st.session_state.current_description = get_node_description("summarize")
        st.session_state.progress = 10
        
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
        st.session_state.step_progress = 1
        update_ui_and_wait()
        return False  # 処理継続
        
    elif st.session_state.step_progress == 1:
        state = add_to_dialog_history(
            state, 
            "summarizer", 
            "要約を生成しています...",
            progress=20
        )
        
        # 状態更新
        st.session_state.state = state
        st.session_state.dialog_history = state["dialog_history"]
        st.session_state.progress = 20
        st.session_state.step_progress = 2
        update_ui_and_wait()
        return False  # 処理継続
        
    elif st.session_state.step_progress == 2:
        state = add_to_dialog_history(
            state, 
            "summarizer", 
            "テキストを分析中...",
            progress=30
        )
        
        # 状態更新
        st.session_state.state = state
        st.session_state.dialog_history = state["dialog_history"]
        st.session_state.progress = 30
        st.session_state.step_progress = 3
        update_ui_and_wait()
        return False  # 処理継続
        
    elif st.session_state.step_progress == 3:
        # 要約生成前メッセージ
        if state["revision_count"] == 1:
            state = add_to_dialog_history(
                state, 
                "summarizer", 
                "初回の要約を作成中...",
                progress=40
            )
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
        st.session_state.step_progress = 4
        update_ui_and_wait()
        return False  # 処理継続
    
    elif st.session_state.step_progress == 4:
        try:
            # 実際の要約生成（API呼び出し）
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
            
            st.session_state.progress = 60
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            
            # ステップの完了
            st.session_state.step_progress = 0  # リセット
            update_ui_and_wait()
            
            # 次のステップへ
            st.session_state.step = "review"
            return True  # 処理完了
            
        except Exception as e:
            # エラーハンドリング
            state = add_to_dialog_history(
                state, 
                "system", 
                f"要約生成中にエラーが発生しました: {str(e)}",
                progress=40
            )
            
            st.session_state.error = str(e)
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            
            # エラー時も次のステップへ
            st.session_state.step_progress = 0  # リセット
            st.session_state.step = "done"
            update_ui_and_wait()
            return True  # 処理完了
    
    return False  # デフォルト：処理継続

def process_review_step():
    """レビューステップを処理"""
    # ステップ進捗管理
    if 'step_progress' not in st.session_state:
        st.session_state.step_progress = 0
    
    state = st.session_state.state
    client = get_client()
    agent = ReviewerAgent(client)
    
    # ステップに基づいた処理
    if st.session_state.step_progress == 0:
        st.session_state.current_node = "review"
        st.session_state.current_description = get_node_description("review")
        st.session_state.progress = 65
        
        # 対話履歴に追加
        state = add_to_dialog_history(
            state, 
            "system", 
            "批評エージェントが要約レビューを実施",
            progress=65
        )
        
        # 状態更新
        st.session_state.state = state
        st.session_state.dialog_history = state["dialog_history"]
        st.session_state.step_progress = 1
        update_ui_and_wait()
        return False  # 処理継続
    
    elif st.session_state.step_progress == 1:
        state = add_to_dialog_history(
            state, 
            "reviewer", 
            "レビューを実施しています...",
            progress=70
        )
        
        st.session_state.progress = 70
        st.session_state.state = state
        st.session_state.dialog_history = state["dialog_history"]
        st.session_state.step_progress = 2
        update_ui_and_wait()
        return False  # 処理継続
    
    elif st.session_state.step_progress == 2:
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
        st.session_state.step_progress = 3
        update_ui_and_wait()
        return False  # 処理継続
    
    elif st.session_state.step_progress == 3:
        try:
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
            st.session_state.step_progress = 4
            update_ui_and_wait()
            return False  # 処理継続
        
        except Exception as e:
            # エラーハンドリング
            state = add_to_dialog_history(
                state, 
                "system", 
                f"レビュー中にエラーが発生しました: {str(e)}",
                progress=75
            )
            
            st.session_state.error = str(e)
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            
            # エラー時はタイトル生成へ
            st.session_state.step_progress = 0  # リセット
            st.session_state.step = "title"
            update_ui_and_wait()
            return True  # 処理完了
    
    elif st.session_state.step_progress == 4:
        # 承認判定
        is_approved = agent.check_approval(state["feedback"], state["revision_count"])
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
        
        # ステップの完了
        st.session_state.step_progress = 0  # リセット
        update_ui_and_wait()
        
        # 次のステップを判断
        if is_approved or state["revision_count"] >= 3:
            st.session_state.step = "title"
        else:
            st.session_state.step = "summarize"
        
        return True  # 処理完了
    
    return False  # デフォルト：処理継続

def process_title_step():
    """タイトル生成ステップを処理"""
    # ステップ進捗管理
    if 'step_progress' not in st.session_state:
        st.session_state.step_progress = 0
    
    state = st.session_state.state
    client = get_client()
    agent = TitleCopywriterAgent(client)
    
    # ステップに基づいた処理
    if st.session_state.step_progress == 0:
        st.session_state.current_node = "title_node"
        st.session_state.current_description = get_node_description("title_node")
        st.session_state.progress = 87
        
        # 対話履歴に追加
        state = add_to_dialog_history(
            state, 
            "system", 
            "タイトル命名エージェントがタイトルを生成します",
            progress=87
        )
        
        # 状態更新
        st.session_state.state = state
        st.session_state.dialog_history = state["dialog_history"]
        st.session_state.step_progress = 1
        update_ui_and_wait()
        return False  # 処理継続
    
    elif st.session_state.step_progress == 1:
        state = add_to_dialog_history(
            state, 
            "title", 
            "タイトルを生成しています...",
            progress=90
        )
        
        st.session_state.progress = 90
        st.session_state.state = state
        st.session_state.dialog_history = state["dialog_history"]
        st.session_state.step_progress = 2
        update_ui_and_wait()
        return False  # 処理継続
    
    elif st.session_state.step_progress == 2:
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
        st.session_state.step_progress = 3
        update_ui_and_wait()
        return False  # 処理継続
    
    elif st.session_state.step_progress == 3:
        try:
            # タイトル生成
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
            
            st.session_state.progress = 96
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            st.session_state.step_progress = 4
            update_ui_and_wait()
            return False  # 処理継続
            
        except Exception as e:
            # エラーハンドリング
            state = add_to_dialog_history(
                state,
                "system",
                f"タイトル生成中にエラーが発生しました: {str(e)}",
                progress=93
            )
            
            st.session_state.error = str(e)
            # エラー時もタイトルとサマリーをデフォルト値で設定
            state["title"] = "エラーが発生しました"
            state["final_summary"] = state.get("summary", "要約が生成できませんでした。")
            
            st.session_state.state = state
            st.session_state.dialog_history = state["dialog_history"]
            
            # 完了ステップへ
            st.session_state.step_progress = 4
            update_ui_and_wait()
            return False  # 続行（完了メッセージを表示）
    
    elif st.session_state.step_progress == 4:
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
        
        # ステップの完了
        st.session_state.step_progress = 0  # リセット
        update_ui_and_wait()
        
        # 次のステップへ
        st.session_state.step = "done"
        return True  # 処理完了
    
    return False  # デフォルト：処理継続

def process_step():
    """現在のステップに基づいて処理を実行"""
    try:
        # 初期化ステップ
        if st.session_state.step == "init":
            process_init_step()
            
        # 要約ステップ
        elif st.session_state.step == "summarize":
            if process_summarize_step():
                pass  # 処理完了、次のステップはprocess_summarize_step内で設定済み
            
        # レビューステップ
        elif st.session_state.step == "review":
            if process_review_step():
                pass  # 処理完了、次のステップはprocess_review_step内で設定済み
            
        # タイトル生成ステップ
        elif st.session_state.step == "title":
            if process_title_step():
                pass  # 処理完了、次のステップはprocess_title_step内で設定済み
            
    except Exception as e:
        st.session_state.error = str(e)
        st.session_state.step = "done"  # エラー時も処理を終了

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
    run_button = st.button(
        "実行", 
        key="run_button", 
        use_container_width=True,
        disabled=st.session_state.step != "idle" and st.session_state.step != "done"
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
            st.session_state.step_progress = 0
            
            # 画面を更新
            st.rerun()
    
    # 現在のステップに基づいて処理を実行
    if st.session_state.step not in ["idle", "done"]:
        process_step()  # 現在のステップを実行
    
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


if __name__ == "__main__":
    render_sidebar()
    render_main_ui()
