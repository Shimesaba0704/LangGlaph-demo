import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
import html
import re

def display_dialog_history(dialog_history: List[Dict[str, Any]], highlight_new: bool = False, last_displayed_index: int = 0):
    """
    タイムライン形式で対話履歴を表示
    """
    if not dialog_history:
        st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
        return
    
    # タイムラインスタイルの定義（一度だけ）
    if "timeline_style_added" not in st.session_state:
        st.markdown("""
        <style>
        .timeline-container {
            position: relative;
            padding-left: 2rem;
            margin-bottom: 1rem;
        }
        .timeline-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0.5rem;
            height: 100%;
            width: 2px;
            background-color: #ddd;
        }
        .timeline-item {
            position: relative;
            margin-bottom: 1.5rem;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -2rem;
            top: 0.25rem;
            width: 1rem;
            height: 1rem;
            border-radius: 50%;
            background-color: #00796B;
        }
        .timeline-content {
            padding: 0.75rem;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .agent-name {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .agent-icon {
            font-size: 1.2rem;
            margin-right: 0.5rem;
            vertical-align: middle;
        }
        .agent-summarizer {
            border-left: 3px solid #009688;
        }
        .agent-reviewer {
            border-left: 3px solid #673AB7;
        }
        .agent-title {
            border-left: 3px solid #FF5722;
        }
        .progress-bar {
            height: 6px;
            background-color: #f0f0f0;
            border-radius: 3px;
            margin-top: 8px;
            overflow: hidden;
        }
        .progress-value {
            height: 100%;
            background-color: #00796B;
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease-out forwards;
        }
        .new-message {
            border-left-width: 3px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.timeline_style_added = True
    
    # 各メッセージを個別に表示
    for i, dialog in enumerate(dialog_history):
        agent_type = dialog.get("agent_type", "unknown")
        content = dialog.get("content", "")
        timestamp = dialog.get("timestamp", "")
        
        # HTMLタグ（<div>タグ）を大文字小文字を無視して除去
        content = re.sub(r'</?div[^>]*>', '', content, flags=re.IGNORECASE)
        
        # HTMLエスケープ処理
        content = html.escape(content)
        
        # 新しいメッセージのハイライト
        is_new = highlight_new and i >= last_displayed_index
        new_class = "new-message" if is_new else ""
        
        # エージェント毎のアイコンとクラス設定
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
        
        # 進捗情報の表示
        progress_html = ""
        if "progress" in dialog and dialog["progress"]:
            progress = dialog["progress"]
            progress_html = f'<div class="progress-bar"><div class="progress-value" style="width: {progress}%"></div></div>'
        
        animation_class = "fade-in" if is_new else ""
        
        # 改行をHTML改行タグに変換
        content = content.replace('\n', '<br>')
        
        st.markdown(
            f"""
            <div class="timeline-container">
                <div class="timeline-item {animation_class}">
                    <div class="timeline-content {agent_class} {new_class}">
                        <div class="agent-name">
                            <span class="agent-icon">{icon}</span> {agent_name}
                            <span style="float: right; font-size: 0.8rem; color: #888;">{timestamp}</span>
                        </div>
                        <div>{content}</div>
                        {progress_html}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def update_dialog_display(placeholder, dialog_history: List[Dict[str, Any]], last_displayed_index: int = 0):
    with placeholder:
        display_dialog_history(
            dialog_history, 
            highlight_new=True, 
            last_displayed_index=last_displayed_index
        )


def add_to_dialog_history(
    state: Dict[str, Any], 
    agent_type: str, 
    content: str, 
    progress: Optional[int] = None
) -> Dict[str, Any]:
    if "dialog_history" not in state:
        state["dialog_history"] = []
    
    # <div>タグの除去（大文字小文字問わず）
    content = re.sub(r'</?div[^>]*>', '', content, flags=re.IGNORECASE)
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
    if "dialog_history" in state and 0 <= index < len(state["dialog_history"]):
        state["dialog_history"][index]["progress"] = progress
    return state
