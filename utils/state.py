from typing import TypedDict, List, Dict, Any, Optional
import streamlit as st
from datetime import datetime

# State の型定義
class State(TypedDict):
    input_text: str
    summary: str
    feedback: str
    previous_summary: str
    previous_feedback: str
    title: str
    final_summary: str
    transcript: List[str]
    revision_count: int 
    approved: bool
    dialog_history: List[Dict[str, Any]]
    last_updated: float  # 最終更新のタイムスタンプを追加


def create_initial_state(input_text: str) -> State:
    """
    ワークフロー用の初期状態を作成
    
    Args:
        input_text: 要約対象のテキスト
        
    Returns:
        State: 初期化された状態オブジェクト
    """
    return {
        "input_text": input_text,
        "summary": "",
        "feedback": "",
        "previous_summary": "",
        "previous_feedback": "",
        "title": "",
        "final_summary": "",
        "transcript": [],
        "revision_count": 0,
        "approved": False,
        "dialog_history": [],
        "last_updated": datetime.now().timestamp()  # 現在のタイムスタンプ
    }


def reset_state() -> None:
    """
    ワークフローの状態をリセット
    """
    if 'workflow_state' in st.session_state:
        del st.session_state.workflow_state


def update_session_state(state: Dict[str, Any]) -> None:
    """
    セッション状態を更新し、UI更新のためのタイムスタンプを設定
    
    Args:
        state: 更新する状態
    """
    # 更新のタイムスタンプを設定
    state["last_updated"] = datetime.now().timestamp()
    
    # セッション状態を更新
    st.session_state.state = state
    
    # 対話履歴を同期
    if "dialog_history" in state:
        st.session_state.dialog_history = state["dialog_history"]
    
    # 進捗状況がある場合は更新
    last_dialog = state.get("dialog_history", [])[-1] if state.get("dialog_history") else None
    if last_dialog and "progress" in last_dialog:
        st.session_state.progress = last_dialog["progress"]
    
    # 最終更新時刻を記録
    st.session_state.last_update_time = datetime.now().timestamp()


def is_update_needed() -> bool:
    """
    UIの更新が必要かどうかを判断
    
    Returns:
        bool: 更新が必要な場合はTrue
    """
    # 最後の更新から一定時間（0.5秒）経過しているか
    if 'last_update_time' not in st.session_state:
        return True
    
    current_time = datetime.now().timestamp()
    elapsed = current_time - st.session_state.last_update_time
    
    # 0.5秒以上経過していれば更新
    return elapsed > 0.5
