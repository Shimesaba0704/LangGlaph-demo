import streamlit as st
from datetime import datetime
from typing import Dict, Any, List


def display_dialog_history(dialog_history: List[Dict[str, Any]]):
    """タイムライン形式で対話履歴を表示"""
    if not dialog_history:
        st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
        return
    
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    for dialog in dialog_history:
        agent_type = dialog.get("agent_type", "unknown")
        content = dialog.get("content", "")
        timestamp = dialog.get("timestamp", "")
        
        # エージェントタイプに基づくスタイル設定
        if agent_type == "summarizer":
            icon = "📝"
            agent_class = "agent-summarizer"
            agent_name = "要約者"
        elif agent_type == "reviewer":
            icon = "⭐"
            agent_class = "agent-reviewer"
            agent_name = "批評家"
        elif agent_type == "title":
            icon = "🏷️"
            agent_class = "agent-title"
            agent_name = "タイトル作成者"
        elif agent_type == "system":
            icon = "🔄"
            agent_class = ""
            agent_name = "システム"
        else:
            icon = "💬"
            agent_class = ""
            agent_name = "不明なエージェント"
        
        st.markdown(f'''
        <div class="timeline-item">
            <div class="timeline-content {agent_class}">
                <div class="agent-name">
                    <span class="agent-icon">{icon}</span> {agent_name}
                    <span style="float: right; font-size: 0.8rem; color: #888;">{timestamp}</span>
                </div>
                <div>{content}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def add_to_dialog_history(state: Dict[str, Any], agent_type: str, content: str) -> Dict[str, Any]:
    """対話履歴に新しいエントリを追加"""
    if "dialog_history" not in state:
        state["dialog_history"] = []
    
    # 現在の日時を取得
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # 対話履歴に追加
    state["dialog_history"].append({
        "agent_type": agent_type,
        "content": content,
        "timestamp": timestamp
    })
    
    return state