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

# CSSスタイル（元のCSS内容をそのまま利用）
st.markdown("""
<style>
/* カラー変数やレイアウト設定など */
/* （元のCSS内容をそのまま利用） */
</style>
""", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from components.workflow_viz import render_workflow_visualization
from components.dialog_history import display_dialog_history, add_to_dialog_history, update_dialog_display

from utils.api_client import initialize_client, get_client
initialize_client()

from graph.workflow import create_workflow_graph
from utils.state import create_initial_state

@auth_required
def render_main_ui():
    st.markdown("""
    <div style="margin: 20px 0 30px 0; padding: 20px 0 15px 0; border-bottom: 2px solid #00796B;">
        <img src="https://langchain-ai.github.io/langgraph/static/wordmark_dark.svg" 
             alt="LangGraph" 
             style="width: 300px; display: block; max-width: 100%;">
    </div>
    """, unsafe_allow_html=True)
    
    # タブの作成
    tab1, tab2 = st.tabs(["ワークフロー実行", "対話ログ"])
    
    # プレースホルダーとセッション状態の初期化
    if 'dialog_placeholder_tab1' not in st.session_state:
        st.session_state.dialog_placeholder_tab1 = st.empty()
    if 'dialog_placeholder_tab2' not in st.session_state:
        st.session_state.dialog_placeholder_tab2 = st.empty()
    if 'result_placeholder' not in st.session_state:
        st.session_state.result_placeholder = st.empty()
    if 'current_dialog_history' not in st.session_state:
        st.session_state.current_dialog_history = []
    if 'last_displayed_history_length' not in st.session_state:
        st.session_state.last_displayed_history_length = 0
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    # セッション上で最終結果を管理
    if "final_state" not in st.session_state:
        st.session_state.final_state = {}

    with tab1:
        st.markdown("""
        <div class="card">
            <p>
                テキスト要約を行う3つのエージェント（要約者、批評家、タイトル作成者）が協力して作業します。
                入力したテキストを要約し、批評・改善を経て、最終的に適切なタイトルがつけられます。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 初期ワークフローの表示
        initial_state = {
            "revision_count": 0,
            "approved": False,
            "dialog_history": []
        }
        
        render_workflow_visualization(initial_state)
        
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
        
        st.subheader("エージェント対話履歴 (リアルタイム)")
        log_container_tab1 = st.container()
        st.session_state.dialog_placeholder_tab1 = log_container_tab1
        
        if st.button("実行", key="run_button", use_container_width=True, disabled=st.session_state.processing):
            if not user_input:
                st.error("文章が入力されていません。")
            else:
                st.session_state.processing = True
                graph = create_workflow_graph()
                client = get_client()
                
                # 対話履歴の初期化
                st.session_state.current_dialog_history = []
                st.session_state.last_displayed_history_length = 0
                
                # 初期状態の作成と対話履歴への追加
                initial_state = create_initial_state(user_input)
                initial_state = add_to_dialog_history(
                    initial_state,
                    "system",
                    "新しいテキストが入力されました。ワークフローを開始します。"
                )
                st.session_state.current_dialog_history = initial_state["dialog_history"]
                
                # セッション状態に最終結果用の初期状態をセット
                st.session_state.final_state = initial_state.copy()
                
                with log_container_tab1:
                    display_dialog_history(st.session_state.current_dialog_history)
                    st.session_state.last_displayed_history_length = len(st.session_state.current_dialog_history)
                with st.session_state.dialog_placeholder_tab2:
                    display_dialog_history(st.session_state.current_dialog_history)
                
                # イベントハンドラ（増分更新）
                def update_ui(event_type, data):
                    if (event_type == "on_node_yield" or event_type == "on_node_end") and "state" in data:
                        node_state = data["state"]
                        if "dialog_history" in node_state:
                            current_history = node_state["dialog_history"]
                            st.session_state.current_dialog_history = current_history
                            with log_container_tab1:
                                display_dialog_history(
                                    current_history,
                                    highlight_new=True,
                                    last_displayed_index=st.session_state.last_displayed_history_length
                                )
                            with st.session_state.dialog_placeholder_tab2:
                                display_dialog_history(
                                    current_history,
                                    highlight_new=True,
                                    last_displayed_index=st.session_state.last_displayed_history_length
                                )
                            st.session_state.last_displayed_history_length = len(current_history)
                            if event_type == "on_node_end":
                                st.session_state.final_state.update(node_state)
                                time.sleep(0.3)
                
                config = {
                    "configurable": {"thread_id": "1"},
                    "events_handlers": [update_ui]
                }
                
                # ワークフロー処理をバックグラウンドスレッドで実行
                def run_workflow():
                    try:
                        result = graph.invoke(initial_state, config)
                        st.session_state.final_state.update(result)
                    except Exception as e:
                        st.session_state.error_message = f"処理中にエラーが発生しました: {str(e)}"
                    finally:
                        st.session_state.processing = False
                
                threading.Thread(target=run_workflow, daemon=True).start()
        
        # processing が真の場合は、1秒待機後にスクリプトを再実行することで最新状態を反映
        if st.session_state.processing:
            time.sleep(1)
            st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.header("エージェント対話ログ")
        st.markdown("""
        <div class="card">
            <h3>LangGraphワークフロー情報</h3>
            <p>エージェント間の対話内容がリアルタイムで表示されます。</p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("実行履歴", expanded=True):
            log_container_tab2 = st.container()
            st.session_state.dialog_placeholder_tab2 = log_container_tab2
            with log_container_tab2:
                if st.session_state.current_dialog_history:
                    display_dialog_history(st.session_state.current_dialog_history)
                else:
                    st.info("実行履歴がありません。ワークフローを実行すると、ここに履歴が表示されます。")
    
    if 'error_message' in st.session_state:
        st.error(st.session_state.error_message)
    
    # 最終結果の表示（処理完了後）
    if not st.session_state.processing and 'result_placeholder' in st.session_state:
        with st.session_state.result_placeholder:
            final_state = st.session_state.final_state
            if "title" in final_state and "final_summary" in final_state:
                st.markdown(f"""
                <div class="result-card">
                    <h2>{final_state['title']}</h2>
                    <div style="padding: 1rem; background-color: #f9f9f9; border-radius: 6px; margin-top: 1rem;">
                        {final_state["final_summary"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("処理は完了しましたが、完全な結果が得られませんでした。")
                st.json({k: v for k, v in final_state.items() if k not in ["dialog_history", "transcript"]})

if __name__ == "__main__":
    render_sidebar()
    render_main_ui()
