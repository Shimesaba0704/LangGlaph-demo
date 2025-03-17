import streamlit as st
from typing import Dict, Any, Optional

def render_workflow_visualization(state: Dict[str, Any], current_node: Optional[str] = None):
    """
    Streamlitネイティブコンポーネントのみを使用したワークフロー可視化
    
    Args:
        state: 現在の状態
        current_node: 現在アクティブなノード名
    """
    # 現在のノードを識別する
    active_node = current_node or "start"
    
    # ノードの順序と状態
    node_order = ["start", "summarize", "review", "title_node", "END"]
    current_index = node_order.index(active_node) if active_node in node_order else 0
    
    # メインワークフローステップ
    st.write("### ワークフロー進行状況")
    cols = st.columns(5)
    
    # ノードの状態とラベルを定義
    nodes = [
        {"id": "start", "emoji": "🚀", "label": "開始"},
        {"id": "summarize", "emoji": "📝", "label": "要約生成"},
        {"id": "review", "emoji": "⭐", "label": "レビュー"},
        {"id": "title_node", "emoji": "🏷️", "label": "タイトル生成"},
        {"id": "END", "emoji": "✅", "label": "完了"}
    ]
    
    # 各ノードを表示
    for i, node in enumerate(nodes):
        with cols[i]:
            # ノードの状態を決定
            if node["id"] == active_node:
                bg_color = "#00796B"
                text_color = "white"
            elif i < current_index:
                bg_color = "#4DB6AC"
                text_color = "white" 
            else:
                bg_color = "#E0F2F1"
                text_color = "#004D40"
                
            # ノードを描画
            st.markdown(
                f"""
                <div style="background-color:{bg_color}; color:{text_color}; padding:10px; 
                border-radius:5px; text-align:center; margin:5px; font-weight:bold;">
                {node["emoji"]} {node["label"]}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # 条件分岐の説明（シンプルなテキストとアイコン）
    st.write("### 分岐条件")
    col1, col2 = st.columns(2)
    
    with col1:
        # 承認分岐
        approval_active = active_node in ["title_node", "END"]
        approval_color = "#1B5E20" if approval_active else "#CCCCCC"
        st.markdown(
            f"""
            <div style="text-align:center; padding:10px;">
                <span style="color:{approval_color}; font-size:20px;">⬆️</span><br>
                <span style="background-color:#E8F5E9; color:#1B5E20; padding:3px 8px; 
                border-radius:10px; font-size:0.9em; border:1px solid #1B5E20;">
                承認時の流れ
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        # 改訂分岐
        revision_active = active_node == "summarize" and state.get("revision_count", 0) > 1
        revision_color = "#F57F17" if revision_active else "#CCCCCC"
        st.markdown(
            f"""
            <div style="text-align:center; padding:10px;">
                <span style="color:{revision_color}; font-size:20px;">↩️</span><br>
                <span style="background-color:#FFF8E1; color:#F57F17; padding:3px 8px; 
                border-radius:10px; font-size:0.9em; border:1px solid #F57F17;">
                改訂要求時の流れ
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # フロー図の説明
    st.markdown(
        """
        <div style="background-color:#F5F5F5; padding:10px; border-radius:5px; margin-top:10px;">
        <strong>ワークフローの流れ:</strong><br>
        1. 開始 → 要約生成：テキストの初回要約を生成<br>
        2. 要約生成 → レビュー：生成された要約の品質を評価<br>
        3. レビュー → タイトル生成：要約が承認された場合<br>
        4. レビュー → 要約生成：改訂が必要な場合<br>
        5. タイトル生成 → 完了：最終結果の生成
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ステータス表示
    st.write("### 現在の状態")
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        # 承認状態
        is_approved = state.get("approved", False)
        if is_approved:
            st.success("✅ 要約承認済み")
        else:
            st.warning("⏳ 要約未承認")
    
    with status_col2:
        # 要約実行回数
        revision_count = state.get("revision_count", 0)
        max_revisions = 3
        st.info(f"🔄 要約実行回数: {revision_count}/{max_revisions}")
