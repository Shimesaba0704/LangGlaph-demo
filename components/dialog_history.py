import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
import html


def display_dialog_history(dialog_history: List[Dict[str, Any]], highlight_new: bool = False, last_displayed_index: int = 0):
    """
    タイムライン形式で対話履歴を表示
    
    Args:
        dialog_history: 対話履歴リスト
        highlight_new: 新しいメッセージをハイライトするかどうか
        last_displayed_index: 最後に表示したインデックス（新しいメッセージのハイライト用）
    """
    if not dialog_history:
        st.info("対話履歴はまだありません。ワークフローを実行すると、ここに対話の流れが表示されます。")
        return
    
    # タイムラインの開始をマークアップではなく直接スタイルを適用する方法で実装
    timeline_container_style = """
    <style>
    .timeline-container {
        position: relative;
        padding-left: 2rem;
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
    </style>
    """
    st.markdown(timeline_container_style, unsafe_allow_html=True)
    
    # コンテナを作成
    timeline_container = st.container()
    
    with timeline_container:
        for i, dialog in enumerate(dialog_history):
            agent_type = dialog.get("agent_type", "unknown")
            content = dialog.get("content", "")
            timestamp = dialog.get("timestamp", "")
            
            # HTMLタグをエスケープ処理
            content = html.escape(content)
            
            # 新しいメッセージ用のクラス
            is_new = highlight_new and i >= last_displayed_index
            new_class = "new-message" if is_new else ""
            
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
            
            # 進捗情報があれば表示
            progress_html = ""
            if "progress" in dialog and dialog["progress"]:
                progress = dialog["progress"]
                progress_html = f'<div class="progress-bar"><div class="progress-value" style="width: {progress}%"></div></div>'
            
            # 新しいメッセージにはアニメーションエフェクトを追加
            animation_class = "fade-in" if is_new else ""
            
            # 改行をHTML改行タグに変換
            content = content.replace('\n', '<br>')
            
            # 各メッセージを独立したマークダウンブロックとして表示
            st.markdown(f'''
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
            ''', unsafe_allow_html=True)
    
    # 新しいメッセージ用のアニメーションCSS
    if highlight_new:
        st.markdown('''
        <style>
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
        
        /* タイムラインアイテムのスタイル */
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
        </style>
        ''', unsafe_allow_html=True)


def update_dialog_display(placeholder, dialog_history: List[Dict[str, Any]], last_displayed_index: int = 0):
    """
    増分更新で対話履歴を表示
    
    Args:
        placeholder: Streamlitのプレースホルダ
        dialog_history: 対話履歴の全リスト
        last_displayed_index: 最後に表示されたインデックス
    """
    # プレースホルダを使って表示を更新
    with placeholder.container():
        st.subheader("エージェント対話履歴 (リアルタイム)")
        
        # 新しいメッセージをハイライト表示
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
    """
    対話履歴に新しいエントリを追加
    
    Args:
        state: 現在の状態
        agent_type: エージェントタイプ
        content: メッセージ内容
        progress: 進捗率（0-100）
    """
    if "dialog_history" not in state:
        state["dialog_history"] = []
    
    # 現在の日時を取得
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # 対話履歴に追加
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
    特定のメッセージの進捗を更新
    
    Args:
        state: 現在の状態
        index: 更新するメッセージのインデックス
        progress: 新しい進捗率（0-100）
    """
    if "dialog_history" in state and 0 <= index < len(state["dialog_history"]):
        state["dialog_history"][index]["progress"] = progress
    
    return state
