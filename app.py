import streamlit as st
from dotenv import load_dotenv
from auth import auth_required
import time

load_dotenv()

from utils.theme import setup_langgraph_theme
setup_langgraph_theme()

from components.sidebar import render_sidebar
from components.workflow_viz import render_workflow_visualization
from components.dialog_history import display_dialog_history, add_to_dialog_history, update_dialog_display

from utils.api_client import initialize_client, get_client
initialize_client()

from graph.workflow import create_workflow_graph

from utils.state import create_initial_state


@auth_required
def render_main_ui():
    """メインUI - タブ式インターフェース"""
    st.markdown("""
    <div style="margin: 20px 0 30px 0; padding: 20px 0 15px 0; border-bottom: 2px solid #00796B;">
        <img src="https://langchain-ai.github.io/langgraph/static/wordmark_dark.svg" 
             alt="LangGraph" 
             style="width: 300px; display: block; max-width: 100%;">
    </div>
    """, unsafe_allow_html=True)
    
    # セッション状態の初期化（タブ追跡用）
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # プレースホルダの初期化
    if 'dialog_placeholder_tab1' not in st.session_state:
        st.session_state.dialog_placeholder_tab1 = st.empty()
    
    if 'dialog_placeholder_tab2' not in st.session_state:
        st.session_state.dialog_placeholder_tab2 = st.empty()
    
    if 'result_placeholder' not in st.session_state:
        st.session_state.result_placeholder = st.empty()
    
    # 対話履歴の初期化
    if 'current_dialog_history' not in st.session_state:
        st.session_state.current_dialog_history = []
    
    if 'last_displayed_history_length' not in st.session_state:
        st.session_state.last_displayed_history_length = 0
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # タブの作成
    tabs = st.tabs(["ワークフロー実行", "対話ログ"])
    
    # タブ選択時の処理
    def handle_tab_change():
        for i, tab in enumerate(tabs):
            if tab._is_focused():
                st.session_state.active_tab = i
                break
    
    # タブ1: ワークフロー実行
    with tabs[0]:
        if st.session_state.active_tab == 0:
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
            
            # ワークフロー図の可視化
            render_workflow_visualization(initial_state)
            
            # 入力エリア
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # 入力テキストの例
            example_texts = [
                "例文を選択してください...",
                "人工知能（AI）は、機械学習、深層学習、自然言語処理などの技術を通じて、人間のような知能を模倣するコンピュータシステムです。近年のAI技術の急速な進歩により、自動運転車、医療診断、翻訳サービスなど、様々な分野で革新的なアプリケーションが開発されています。AIの発展は私たちの生活や仕事のあり方を大きく変えつつありますが、同時にプライバシーや雇用への影響など、社会的・倫理的な課題も提起しています。",
                "宇宙探査は人類の好奇心と技術の集大成です。太陽系の惑星や衛星への無人探査機の送付から、国際宇宙ステーションでの有人ミッション、さらには将来の火星有人探査計画まで、私たちは宇宙への理解を深め続けています。これらのミッションから得られる科学的データは、地球外生命の可能性の探索や、宇宙の起源についての理解を深めるのに役立っています。宇宙探査は技術革新を促進し、地球上の課題解決にも応用される新技術の開発につながっています。"
            ]
            
            # サンプルテキスト選択ドロップダウン
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
            
            # 選択されたサンプルテキストまたは空の入力欄を表示
            if selected_example != example_texts[0]:
                default_text = selected_example
            else:
                default_text = ""
            
            user_input = st.text_area(
                "要約したい文章を入力してください", 
                value=default_text,
                height=150, 
                key="input_text",
                label_visibility="collapsed"
            )
            
            # 対話ログの表示エリア
            st.markdown("<h3>エージェント対話履歴 (リアルタイム)</h3>", unsafe_allow_html=True)
            # リアルタイムログ表示用コンテナ（タブ1用）
            log_container_tab1 = st.container(height=400)
            st.session_state.dialog_placeholder_tab1 = log_container_tab1
            
            # 実行ボタン
            if st.button("実行", key="run_button", use_container_width=True, disabled=st.session_state.processing):
                if not user_input:
                    st.error("文章が入力されていません。")
                else:
                    # 処理中フラグをセット
                    st.session_state.processing = True
                    
                    # グラフを取得
                    graph = create_workflow_graph()
                    client = get_client()
                    
                    # 実行前に対話履歴をクリア
                    st.session_state.current_dialog_history = []
                    st.session_state.last_displayed_history_length = 0
                    
                    # 初期状態の作成
                    initial_state = create_initial_state(user_input)
                    
                    # 対話履歴に追加 - 入力テキスト
                    initial_state = add_to_dialog_history(
                        initial_state,
                        "system",
                        "新しいテキストが入力されました。ワークフローを開始します。"
                    )
                    
                    # 最初の対話履歴を表示
                    st.session_state.current_dialog_history = initial_state["dialog_history"]
                    
                    # タブ1のコンテナ内に対話履歴を表示
                    with log_container_tab1:
                        display_dialog_history(st.session_state.current_dialog_history)
                        st.session_state.last_displayed_history_length = len(st.session_state.current_dialog_history)
                    
                    # 最終状態を追跡する変数
                    final_state = initial_state.copy()
                    
                    # イベントハンドラ設定 (増分更新)
                    def update_ui(event_type, data):
                        # on_node_yieldとon_node_endを拾って増分更新
                        if (event_type == "on_node_yield" or event_type == "on_node_end") and "state" in data:
                            node_state = data["state"]
                            if "dialog_history" in node_state:
                                current_history = node_state["dialog_history"]
                                st.session_state.current_dialog_history = current_history
                                
                                # タブ1のコンテナを更新
                                with log_container_tab1:
                                    # 履歴全体を表示し、新しいメッセージのみハイライト
                                    display_dialog_history(
                                        current_history, 
                                        highlight_new=True, 
                                        last_displayed_index=st.session_state.last_displayed_history_length
                                    )
                                
                                # タブ2の更新はタブ2が表示されている場合のみ
                                if 'dialog_placeholder_tab2' in st.session_state and st.session_state.dialog_placeholder_tab2:
                                    with st.session_state.dialog_placeholder_tab2:
                                        display_dialog_history(
                                            current_history,
                                            highlight_new=True,
                                            last_displayed_index=st.session_state.last_displayed_history_length
                                        )
                                
                                st.session_state.last_displayed_history_length = len(current_history)
                                
                                # ノードが完了した場合は状態を更新
                                if event_type == "on_node_end":
                                    final_state.update(node_state)
                                    
                                    # 少し待機して進捗の視覚的効果を確認できるようにする
                                    time.sleep(0.3)
                    
                    config = {
                        "configurable": {"thread_id": "1"},
                        "events_handlers": [update_ui]
                    }

                    with st.spinner(f"テキスト処理中..."):
                        try:
                            # グラフ実行
                            result = graph.invoke(initial_state, config)
                            final_state.update(result)
                        except Exception as e:
                            st.error(f"処理中にエラーが発生しました: {str(e)}")
                            st.exception(e)
                        finally:
                            # 処理完了後、フラグをリセット
                            st.session_state.processing = False
                    
                    st.success("処理完了！")
                    
                    # 最終結果の表示
                    result_container = st.container()
                    with result_container:
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
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # タブ2: 対話ログ
    with tabs[1]:
        if st.session_state.active_tab == 1:
            st.header("エージェント対話ログ")
            
            # 情報セクション
            st.markdown("""
            <div class="card">
                <h3>LangGraphワークフロー情報</h3>
                <p>エージェント間の対話内容がリアルタイムで表示されます。</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 詳細ログセクション（常に展開された状態）
            st.subheader("実行履歴")
            
            # リアルタイムログ表示用コンテナ（タブ2用）
            log_container_tab2 = st.container(height=500)
            st.session_state.dialog_placeholder_tab2 = log_container_tab2
            
            # 対話履歴の表示
            with log_container_tab2:
                if st.session_state.current_dialog_history:
                    st.subheader("エージェント対話履歴 (リアルタイム)")
                    display_dialog_history(st.session_state.current_dialog_history)
                else:
                    st.info("実行履歴がありません。ワークフローを実行すると、ここに履歴が表示されます。")

    # タブの変更を検知
    handle_tab_change()

# サイドバーとメインUIの描画
if __name__ == "__main__":
    render_sidebar()
    render_main_ui()
