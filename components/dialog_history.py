import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional

def display_dialog_history(dialog_history: List[Dict[str, Any]]):
    """
    洗練された対話履歴表示
    """
    if not dialog_history:
        st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
        return
    
    # カスタムCSSスタイル
    st.markdown("""
    <style>
    .dialog-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .agent-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 5px;
    }
    .agent-name {
        font-weight: bold;
        display: flex;
        align-items: center;
    }
    .agent-icon {
        margin-right: 8px;
        font-size: 18px;
    }
    .agent-timestamp {
        font-size: 12px;
        color: #888;
    }
    .agent-content {
        line-height: 1.5;
    }
    .agent-summarizer {
        border-left: 4px solid #009688;
    }
    .agent-reviewer {
        border-left: 4px solid #673AB7;
    }
    .agent-title {
        border-left: 4px solid #FF5722;
    }
    .agent-system {
        border-left: 4px solid #9E9E9E;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 各対話メッセージを表示
    for dialog in dialog_history:
        agent_type = dialog.get("agent_type", "unknown")
        content = dialog.get("content", "")
        timestamp = dialog.get("timestamp", "")
        
        # エージェント毎の設定
        if agent_type == "summarizer":
            emoji = "📝"
            agent_name = "要約者"
            agent_class = "agent-summarizer"
        elif agent_type == "reviewer":
            emoji = "⭐"
            agent_name = "批評家"
            agent_class = "agent-reviewer"
        elif agent_type == "title":
            emoji = "🏷️"
            agent_name = "タイトル作成者"
            agent_class = "agent-title"
        elif agent_type == "system":
            emoji = "🔄"
            agent_name = "システム"
            agent_class = "agent-system"
        else:
            emoji = "💬"
            agent_name = "不明なエージェント"
            agent_class = ""
        
        # 対話カードの表示
        st.markdown(f"""
        <div class="dialog-card {agent_class}">
            <div class="agent-header">
                <div class="agent-name">
                    <span class="agent-icon">{emoji}</span> {agent_name}
                </div>
                <span class="agent-timestamp">{timestamp}</span>
            </div>
            <div class="agent-content">
                {content.replace('\n', '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 進捗がある場合は表示（オプション）
        if "progress" in dialog and dialog["progress"]:
            progress = dialog["progress"]
            st.progress(progress / 100)


def add_to_dialog_history(
    state: Dict[str, Any], 
    agent_type: str, 
    content: str, 
    progress: Optional[int] = None
) -> Dict[str, Any]:
    """
    対話履歴にメッセージを追加
    """
    if "dialog_history" not in state:
        state["dialog_history"] = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    state["dialog_history"].append({
        "agent_type": agent_type,
        "content": content,
        "timestamp": timestamp,
        "progress": progress
    })
    
    return state


def update_progress(
    state: Dict[str, Any], 
    index: int, 
    progress: int
) -> Dict[str, Any]:
    """
    指定されたインデックスのメッセージの進捗を更新
    """
    if "dialog_history" in state and 0 <= index < len(state["dialog_history"]):
        state["dialog_history"][index]["progress"] = progress
    return state
