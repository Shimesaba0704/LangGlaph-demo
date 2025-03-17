import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional

def display_dialog_history(dialog_history: List[Dict[str, Any]]):
    """
    シンプルな形式で対話履歴を表示
    """
    if not dialog_history:
        st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
        return
    
    # 各エージェントごとに色分けされた簡易表示
    for dialog in dialog_history:
        agent_type = dialog.get("agent_type", "unknown")
        content = dialog.get("content", "")
        timestamp = dialog.get("timestamp", "")
        
        # エージェント毎の設定
        if agent_type == "summarizer":
            emoji = "📝"
            agent_name = "要約者"
            bg_color = "#E0F2F1"
            border_color = "#009688"
        elif agent_type == "reviewer":
            emoji = "⭐"
            agent_name = "批評家"
            bg_color = "#EDE7F6"
            border_color = "#673AB7"
        elif agent_type == "title":
            emoji = "🏷️"
            agent_name = "タイトル作成者"
            bg_color = "#FBE9E7"
            border_color = "#FF5722"
        elif agent_type == "system":
            emoji = "🔄"
            agent_name = "システム"
            bg_color = "#F5F5F5"
            border_color = "#9E9E9E"
        else:
            emoji = "💬"
            agent_name = "不明なエージェント"
            bg_color = "#F5F5F5"
            border_color = "#9E9E9E"
        
        # メッセージコンテナの表示
        st.markdown(f"**{emoji} {agent_name}** - *{timestamp}*")
        
        # シンプルな枠線付きエリアでコンテンツを表示
        st.markdown(
            f"""
            <div style="padding: 10px; background-color: {bg_color}; 
                        border-left: 3px solid {border_color}; 
                        margin-bottom: 15px; border-radius: 0 5px 5px 0;">
                {content}
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # 進捗バーがあれば表示（オプション）
        if "progress" in dialog and dialog["progress"]:
            progress = dialog["progress"]
            # 進捗バーはStreamlitのコンポーネントを使用
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
