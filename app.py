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

/* 進捗インジケーター関連のスタイル追加 */
.task-progress {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    animation: fadeIn 0.5s ease-out forwards;
}
.task-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background-color: #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
    font-size: 12px;
}
.task-icon.active {
    background-color: #00796B;
    color: white;
    animation: pulse 1.5s infinite;
}
.task-icon.completed {
    background-color: #4DB6AC;
    color: white;
}
.task-label {
    flex-grow: 1;
}
.task-status {
    font-size: 12px;
    color: #888;
}
.task-status.active {
    color: #00796B;
    font-weight: bold;
}
@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.processing-indicator {
    display: flex;
    align-items: center;
    background-color: #E0F2F1;
    padding: 10px 15px;
    border-radius: 6px;
    margin-bottom: 15px;
    border-left: 4px solid #00796B;
    animation: pulse 1.5s infinite;
}
.processing-icon {
    margin-right: 10px;
    font-size: 18px;
    color: #00796B;
}
.latest-action {
    margin-top: 10px;
    padding: 8px 12px;
    background-color: #FFF8E1;
    border-left: 4px solid #FFC107;
    border-radius: 4px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from components.workflow_viz import render_workflow_visualization
from components.dialog_history import display_dialog_history, add_to_dialog_history

from utils.api_client import initialize_client, get_client
initialize_client()

from graph.workflow import create_workflow_graph
from utils.state import create_initial_state

# 初回読み込み時にprocessingをリセット
if 'processing' not in st.session_state:
    st.session_state.processing = False
# 明示的にprocessingをリセットするフラグ
if 'reset_processing' in st.session_state and st.session_state.reset_processing:
    st.session_state.processing = False
    st.session_state.reset_processing = False
# 最新のアクション状態を追跡
if 'latest_action' not in st.session_state:
    st.session_state.latest_action = ""

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
    
    # プレースホルダーとセッション状態の初期化
    if 'result_placeholder' not in st.session_state:
        st.session_state.result_placeholder = st.empty()
    if 'current_dialog_history' not in st.session_state:
        st.session_state.current_dialog_history = []
    # セッション上で最終結果を管理
    if "final_state" not in st.session_state:
        st.session_state.final_state = {}

    # メイン画面（タブなし）
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
    
    # 実行ボタン - 処理状態に関わらず常に有効化
    run_button = st.button(
        "実行", 
        key="run_button", 
        use_container_width=True
    )
    
    # エージェント対話履歴セクション
    st.subheader("エージェント対話履歴")
    
    # 進捗状況表示用コンテナを追加
    progress_status_container = st.container()
    dialog_container = st.container()
    
    # 実行ボタンが押された場合の処理
    if run_button:
        if not user_input:
            st.error("文章が入力されていません。")
        elif st.session_state.processing:
            st.warning("すでに処理中です。完了までお待ちください。")
        else:
            st.session_state.processing = True
            graph = create_workflow_graph()
            client = get_client()
            
            # 対話履歴の初期化
            st.session_state.current_dialog_history = []
            
            # 初期状態の作成と対話履歴への追加
            initial_state = create_initial_state(user_input)
            initial_state = add_to_dialog_history(
                initial_state,
                "system",
                "新しいテキストが入力されました。ワークフローを開始します。",
                progress=5  # 初期進捗状態
            )
            st.session_state.current_dialog_history = initial_state["dialog_history"]
            
            # セッション状態に最終結果用の初期状態をセット
            st.session_state.final_state = initial_state.copy()
            # 最新アクション状態をリセット
            st.session_state.latest_action = "ワークフローを開始しています..."
            
            # ワークフロー処理をバックグラウンドスレッドで実行
            def run_workflow():
                try:
                    # ワークフローの実行
                    for event_type, data in graph.stream(initial_state):
                        if event_type == "on_chain_end":
                            # ノード実行終了時
                            current_node = data.get("current_node", "")
                            st.session_state.latest_action = get_node_description(current_node)
                            
                            # 対話履歴も更新
                            if "dialog_history" in data:
                                st.session_state.current_dialog_history = data["dialog_history"]
                            
                            # 一時的な状態更新
                            st.session_state.final_state.update(data)
                            # 0.5秒待機してUI更新に時間を与える
                            time.sleep(0.5)
                    
                    # 最終結果の設定
                    final_result = graph.get_state()
                    st.session_state.final_state.update(final_result)
                    if "dialog_history" in final_result:
                        st.session_state.current_dialog_history = final_result["dialog_history"]
                    st.session_state.latest_action = "処理が完了しました"
                except Exception as e:
                    st.session_state.error_message = f"処理中にエラーが発生しました: {str(e)}"
                    st.session_state.latest_action = "エラーが発生しました"
                finally:
                    st.session_state.processing = False
                    st.session_state.reset_processing = True
                    st.rerun()
            
            threading.Thread(target=run_workflow, daemon=True).start()
    
    # 処理中の表示
    with progress_status_container:
        if st.session_state.processing:
            # 現在のワークフロー状態
            current_state = st.session_state.final_state
            current_node = current_state.get("current_node", "")
            revision_count = current_state.get("revision_count", 0)
            
            # 進行中プロセスの視覚的インジケーター表示
            st.markdown(f"""
            <div class="processing-indicator">
                <div class="processing-icon">⚙️</div>
                <div>
                    <strong>処理中...</strong> ワークフローを実行しています
                    <div class="latest-action">{st.session_state.latest_action}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 各タスクの状態を表示
            st.markdown("<div style='background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            st.markdown("#### 実行タスクの状態")
            
            # 各タスクのステータス判定
            tasks = [
                {"id": "summarize", "label": "要約生成", "icon": "📝"},
                {"id": "review", "label": "品質レビュー", "icon": "⭐"},
                {"id": "title_node", "label": "タイトル生成", "icon": "🏷️"},
                {"id": "END", "label": "処理完了", "icon": "✅"}
            ]
            
            for task in tasks:
                task_id = task["id"]
                label = task["label"]
                icon = task["icon"]
                
                # タスクの状態を判定
                status = "待機中"
                icon_class = ""
                status_class = ""
                
                if current_node == task_id:
                    status = "実行中"
                    icon_class = "active"
                    status_class = "active"
                elif task_id == "summarize" and revision_count > 0:
                    status = f"完了 (改訂 {revision_count}回)"
                    icon_class = "completed"
                elif current_node == "review" and task_id == "summarize":
                    status = "完了"
                    icon_class = "completed"
                elif current_node == "title_node" and (task_id == "summarize" or task_id == "review"):
                    status = "完了"
                    icon_class = "completed"
                elif current_node == "END" and task_id != "END":
                    status = "完了"
                    icon_class = "completed"
                
                # タスク状態の表示
                st.markdown(f"""
                <div class="task-progress">
                    <div class="task-icon {icon_class}">{icon}</div>
                    <div class="task-label">{label}</div>
                    <div class="task-status {status_class}">{status}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 現在のステップに関する追加情報
            if current_node == "summarize":
                step_info = "テキストを分析し、要約を生成しています..."
            elif current_node == "review":
                step_info = "要約の品質を評価しています..."
            elif current_node == "title_node":
                step_info = "要約に適切なタイトルを付けています..."
            elif current_node == "END":
                step_info = "すべてのタスクが完了しました！"
            else:
                step_info = "ワークフローを初期化しています..."
                
            st.markdown(f"<div style='margin-top: 10px; font-style: italic;'>{step_info}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # スピナーを表示
            st.spinner("実行中...")
            
    # 対話履歴の表示
    with dialog_container:
        if st.session_state.processing or st.session_state.current_dialog_history:
            display_dialog_history(st.session_state.current_dialog_history)
        else:
            st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
