import streamlit as st
from typing import Dict, Any, Optional

def render_workflow_visualization(state: Dict[str, Any], current_node: Optional[str] = None):
    """
    シンプルなワークフロー可視化
    
    Args:
        state: 現在の状態
        current_node: 現在アクティブなノード名
    """
    # ノードの状態マッピング
    nodes = [
        {"id": "start", "name": "開始"},
        {"id": "summarize", "name": "要約生成"},
        {"id": "review", "name": "レビュー"},
        {"id": "title_node", "name": "タイトル生成"},
        {"id": "END", "name": "完了"}
    ]
    
    # 現在のノードを識別する
    active_node = current_node or "start"
    
    # ステータス表示
    st.markdown("### ワークフロー状態")
    
    # ステップ進捗の横並び表示
    cols = st.columns(len(nodes))
    
    for i, node in enumerate(nodes):
        with cols[i]:
            # 現在のノードとアクティブノードの比較
            is_active = node["id"] == active_node
            is_completed = False
            
            # 完了したノードの判定
            if active_node == "END":
                # 全て完了
                is_completed = True
            elif i < [n["id"] for n in nodes].index(active_node):
                # 現在のノードより前のノードは完了
                is_completed = True
            
            # 表示スタイルの設定
            if is_active:
                # アクティブノード
                bg_color = "#00796B"
                text_color = "white"
                emoji = "➡️"
            elif is_completed:
                # 完了ノード
                bg_color = "#4DB6AC"
                text_color = "white"
                emoji = "✅"
            else:
                # 未完了ノード
                bg_color = "#E0F2F1"
                text_color = "#004D40" 
                emoji = "⏹️"
            
            # ノード表示
            st.markdown(
                f"""
                <div style="
                    background-color: {bg_color}; 
                    color: {text_color}; 
                    padding: 10px 5px; 
                    border-radius: 5px; 
                    text-align: center;
                    font-weight: {'bold' if is_active else 'normal'};
                    margin: 2px;
                ">
                    {emoji} {node["name"]}
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # ステータスバッジ表示
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        status_text = "承認済" if state.get("approved", False) else "未承認"
        status_color = "#1B5E20" if state.get("approved", False) else "#F57F17"
        st.markdown(
            f"""
            <div style="
                display: inline-block;
                padding: 5px 10px;
                background-color: {status_color}20;
                color: {status_color};
                border-radius: 5px;
                font-weight: bold;
            ">
                状態: {status_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        revision_count = state.get("revision_count", 0)
        max_revisions = 3  # 最大改訂回数
        st.markdown(
            f"""
            <div style="
                display: inline-block;
                padding: 5px 10px;
                background-color: #E0F2F1;
                color: #004D40;
                border-radius: 5px;
                font-weight: bold;
                text-align: right;
                float: right;
            ">
                要約実行回数: {revision_count}/{max_revisions}
            </div>
            """,
            unsafe_allow_html=True
        )
