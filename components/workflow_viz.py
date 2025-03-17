import streamlit as st
from typing import Dict, Any, Optional

def render_workflow_visualization(state: Dict[str, Any], current_node: Optional[str] = None):
    """
    より明確なフロー表現を持つワークフロー可視化
    
    Args:
        state: 現在の状態
        current_node: 現在アクティブなノード名
    """
    # 現在のノードを識別する
    active_node = current_node or "start"
    
    # カスタムCSSを適用
    st.markdown("""
    <style>
    .workflow-container {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .workflow-step {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .workflow-node {
        padding: 10px 15px;
        border-radius: 5px;
        text-align: center;
        margin: 5px;
        font-weight: bold;
        min-width: 120px;
    }
    .node-active {
        background-color: #00796B;
        color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .node-completed {
        background-color: #4DB6AC;
        color: white;
    }
    .node-pending {
        background-color: #E0F2F1;
        color: #004D40;
    }
    .workflow-arrow {
        font-size: 24px;
        color: #00796B;
        margin: 0 10px;
    }
    .workflow-branch {
        display: flex;
        justify-content: center;
        position: relative;
        margin: 10px 0;
    }
    .branch-label {
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        margin: 0 5px;
    }
    .branch-approval {
        background-color: #E8F5E9;
        color: #1B5E20;
        border: 1px solid #1B5E20;
    }
    .branch-revision {
        background-color: #FFF8E1;
        color: #F57F17;
        border: 1px solid #F57F17;
    }
    .branch-active {
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        font-weight: bold;
    }
    .branch-line {
        position: absolute;
        background-color: #00796B;
        z-index: 0;
    }
    .branch-horizontal {
        height: 2px;
        top: 50%;
    }
    .branch-vertical {
        width: 2px;
    }
    .workflow-status {
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 新しいレイアウト - 水平フロー + 垂直分岐
    st.markdown('<div class="workflow-container">', unsafe_allow_html=True)
    
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
    
    # 承認分岐がアクティブかどうか
    is_approval_active = active_node in ["title_node", "END"]
    
    # 改訂分岐がアクティブかどうか
    is_revision_active = active_node == "summarize" and state.get("revision_count", 0) > 1
    
    # メインフロー部分
    st.markdown('''
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
        <div class="workflow-step">
            <div class="workflow-node {start_state}">🚀 開始</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-step">
            <div class="workflow-node {summarize_state}">📝 要約生成</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-step">
            <div class="workflow-node {review_state}">⭐ レビュー</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-step">
            <div class="workflow-node {title_state}">🏷️ タイトル生成</div>
        </div>
        <div class="workflow-arrow">→</div>
        <div class="workflow-step">
            <div class="workflow-node {end_state}">✅ 完了</div>
        </div>
    </div>
    '''.format(
        start_state=get_node_state("start"),
        summarize_state=get_node_state("summarize"),
        review_state=get_node_state("review"),
        title_state=get_node_state("title_node"),
        end_state=get_node_state("END")
    ), unsafe_allow_html=True)
    
    # 分岐部分（より視覚的に明確に）
    branch_html = f'''
    <div style="position: relative; width: 100%; height: 100px; margin: 0 auto;">
        <!-- レビューの位置マーカー -->
        <div style="position: absolute; left: 50%; transform: translateX(-50%); top: 0; width: 2px; height: 20px; background-color: #00796B;"></div>
        
        <!-- 承認分岐 -->
        <div style="position: absolute; left: 60%; top: 20px; transform: translateX(-50%);">
            <span class="branch-label branch-approval {'' if is_approval_active else ''}">
                承認時
            </span>
            <div style="position: absolute; left: 50%; top: 100%; transform: translateY(-50%); width: 0; height: 0; 
                 border-left: 8px solid transparent; border-right: 8px solid transparent; 
                 border-top: 8px solid {'#1B5E20' if is_approval_active else '#CCCCCC'};">
            </div>
        </div>
        
        <!-- 改訂要求分岐 -->
        <div style="position: absolute; left: 40%; top: 20px; transform: translateX(-50%);">
            <span class="branch-label branch-revision {'' if is_revision_active else ''}">
                改訂要求
            </span>
            <div style="position: absolute; left: 50%; top: 100%; transform: translateX(-50%); width: 0; height: 0; 
                 border-left: 8px solid transparent; border-right: 8px solid transparent; 
                 border-top: 8px solid {'#F57F17' if is_revision_active else '#CCCCCC'};">
            </div>
        </div>
        
        <!-- 分岐線 -->
        <div style="position: absolute; left: 40%; top: 50px; width: 20%; height: 2px; 
             background-color: {'#F57F17' if is_revision_active else '#CCCCCC'};">
        </div>
        <div style="position: absolute; left: 40%; top: 50px; width: 2px; height: 30px; 
             background-color: {'#F57F17' if is_revision_active else '#CCCCCC'};">
        </div>
        
        <!-- 承認分岐線 -->
        <div style="position: absolute; left: 60%; top: 50px; width: 2px; height: 30px; 
             background-color: {'#1B5E20' if is_approval_active else '#CCCCCC'};">
        </div>
        
        <!-- 分岐先を示す矢印 -->
        <div style="position: absolute; left: 40%; top: 85px; transform: translateX(-50%);">
            <span style="font-size: 20px; color: {'#F57F17' if is_revision_active else '#CCCCCC'};">↩︎</span>
        </div>
    </div>
    '''
    
    st.markdown(branch_html, unsafe_allow_html=True)
    
    # ステータス表示
    st.markdown('<div class="workflow-status">', unsafe_allow_html=True)
    
    # 承認状態
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
    
    # 要約実行回数
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
        ">
            要約実行回数: {revision_count}/{max_revisions}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)  # workflow-status
    st.markdown('</div>', unsafe_allow_html=True)  # workflow-container
