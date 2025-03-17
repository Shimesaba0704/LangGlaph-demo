import streamlit as st
from typing import Dict, Any, Optional

def render_workflow_visualization(state: Dict[str, Any], current_node: Optional[str] = None):
    """
    テキスト主体のシンプルなワークフロー可視化
    
    Args:
        state: 現在の状態
        current_node: 現在アクティブなノード名
    """
    # 現在のノードを識別する
    active_node = current_node or "start"
    
    # ノードの順序と状態
    node_order = ["start", "summarize", "review", "title_node", "END"]
    current_index = node_order.index(active_node) if active_node in node_order else 0
    
    # ステップの定義
    nodes = [
        {"id": "start", "emoji": "🚀", "label": "開始"},
        {"id": "summarize", "emoji": "📝", "label": "要約生成"},
        {"id": "review", "emoji": "⭐", "label": "レビュー"},
        {"id": "title_node", "emoji": "🏷️", "label": "タイトル生成"},
        {"id": "END", "emoji": "✅", "label": "完了"}
    ]
    
    # メインワークフローステップの表示
    st.write("### ワークフロー進行状況")
    cols = st.columns(5)
    
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
    
    # ワークフローの説明をテキストのみで表示
    st.write("ワークフローの流れ")
    
    st.markdown(
        """
        <div style="background-color:#F5F5F5; padding:15px; border-radius:5px; margin:10px 0;">
        <strong>基本フロー:</strong><br>
        1. <strong>開始</strong> → <strong>要約生成</strong>：テキストの初回要約を生成<br>
        2. <strong>要約生成</strong> → <strong>レビュー</strong>：生成された要約の品質を評価<br>
        3. <strong>レビュー</strong> → <strong>タイトル生成</strong>：要約が<span style="color:#1B5E20; font-weight:bold;">承認</span>された場合<br>
        4. <strong>レビュー</strong> → <strong>要約生成</strong>：<span style="color:#F57F17; font-weight:bold;">改訂が必要</span>な場合（フィードバックをもとに再度要約）<br>
        5. <strong>タイトル生成</strong> → <strong>完了</strong>：最終結果の生成
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 現在の状況を表示
    st.write("### 現在の状態")
    
    current_status = ""
    if active_node == "start":
        current_status = "ワークフローを開始します"
    elif active_node == "summarize":
        if state.get("revision_count", 0) <= 1:
            current_status = "最初の要約を生成しています"
        else:
            current_status = "レビューに基づいて要約を改訂しています"
    elif active_node == "review":
        current_status = "生成された要約をレビューしています"
    elif active_node == "title_node":
        current_status = "承認された要約にタイトルを付けています"
    elif active_node == "END":
        current_status = "処理が完了しました"
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        # 承認状態
        is_approved = state.get("approved", False)
        if is_approved:
            st.success("✅ 要約承認済み")
        else:
            st.warning("⏳ 要約未承認")
        
        # 現在の状況
        st.info(f"💬 {current_status}")
    
    with status_col2:
        # 要約実行回数
        revision_count = state.get("revision_count", 0)
        max_revisions = 3
        
        # プログレスバーでの視覚化
        progress_percentage = min(revision_count / max_revisions, 1.0)
        st.write(f"🔄 要約実行回数: {revision_count}/{max_revisions}")
        st.progress(progress_percentage)
        
        # 最大回数に達したかどうか
        if revision_count >= max_revisions:
            st.warning("⚠️ 最大改訂回数に達しました。自動的に承認されます。")
