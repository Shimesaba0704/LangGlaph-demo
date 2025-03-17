import streamlit as st
from typing import Dict, Any, Optional

def render_workflow_visualization(state: Dict[str, Any], current_node: Optional[str] = None):
    """
    条件分岐を含むワークフロー可視化
    
    Args:
        state: 現在の状態
        current_node: 現在アクティブなノード名
    """
    # 現在のノードを識別する
    active_node = current_node or "start"
    
    # カスタムCSSを適用
    st.markdown("""
    <style>
    .workflow-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .workflow-node {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 5px;
        font-weight: bold;
    }
    .node-active {
        background-color: #00796B;
        color: white;
    }
    .node-completed {
        background-color: #4DB6AC;
        color: white;
    }
    .node-pending {
        background-color: #E0F2F1;
        color: #004D40;
    }
    .branch-line {
        height: 2px;
        background-color: #00796B;
        margin: 5px 0;
    }
    .branch-label {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        display: inline-block;
        margin: 2px 0;
    }
    .branch-approval {
        background-color: #E8F5E9;
        color: #1B5E20;
    }
    .branch-revision {
        background-color: #FFF8E1;
        color: #F57F17;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ワークフローカードの開始
    st.markdown('<div class="workflow-card">', unsafe_allow_html=True)
    
    # メインのワークフロー
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.5, 1, 1])
    
    # 各ノードのアクティブ状態を判定
    def get_node_state(node_id):
        if node_id == active_node:
            return "node-active"
        
        # ノードの順序
        node_order = ["start", "summarize", "review", "title_node", "END"]
        current_index = node_order.index(active_node) if active_node in node_order else 0
        node_index = node_order.index(node_id) if node_id in node_order else 0
        
        # 現在のノードより前のノードは完了
        if node_index < current_index:
            return "node-completed"
        
        # それ以外は未完了
        return "node-pending"
    
    # 開始ノード
    with col1:
        st.markdown(f'<div class="workflow-node {get_node_state("start")}">🚀 開始</div>', unsafe_allow_html=True)
    
    # 要約ノード
    with col2:
        st.markdown(f'<div class="workflow-node {get_node_state("summarize")}">📝 要約生成</div>', unsafe_allow_html=True)
    
    # レビューノード（条件分岐あり）
    with col3:
        st.markdown(f'<div class="workflow-node {get_node_state("review")}">⭐ レビュー</div>', unsafe_allow_html=True)
        
        # 条件分岐表示
        st.markdown('<div style="position: relative; padding: 0 10px;">', unsafe_allow_html=True)
        
        # 承認分岐（上方向）
        if active_node == "title_node" or active_node == "END":
            branch_color = "#1B5E20"  # アクティブな場合の色
        else:
            branch_color = "#CCCCCC"  # 非アクティブな場合の色
            
        st.markdown(f'<div style="text-align: right;"><span class="branch-label branch-approval">承認時</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="branch-line" style="background-color: {branch_color};"></div>', unsafe_allow_html=True)
        
        # 改訂要求分岐（下方向）
        if active_node == "summarize" and state.get("revision_count", 0) > 1:
            branch_color = "#F57F17"  # アクティブな場合の色
        else:
            branch_color = "#CCCCCC"  # 非アクティブな場合の色
            
        st.markdown(f'<div style="text-align: right;"><span class="branch-label branch-revision">改訂要求</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="branch-line" style="background-color: {branch_color};"></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # タイトル生成ノード
    with col4:
        st.markdown(f'<div class="workflow-node {get_node_state("title_node")}">🏷️ タイトル生成</div>', unsafe_allow_html=True)
    
    # 完了ノード
    with col5:
        st.markdown(f'<div class="workflow-node {get_node_state("END")}">✅ 完了</div>', unsafe_allow_html=True)
    
    # ワークフローカードの終了
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ステータスバッジの表示
    col_left, col_right = st.columns(2)
    
    with col_left:
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
    
    with col_right:
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
