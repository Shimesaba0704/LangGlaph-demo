from typing import TypedDict, List, Dict, Any, Optional
import streamlit as st

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
        "dialog_history": []
    }


def reset_state() -> None:
    """
    ワークフローの状態をリセット
    """
    if 'workflow_state' in st.session_state:
        del st.session_state.workflow_state