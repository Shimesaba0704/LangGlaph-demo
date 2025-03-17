import streamlit as st
from typing import Dict, Any, Generator
from utils.api_client import get_client
from agents.summarizer import SummarizerAgent
from agents.reviewer import ReviewerAgent
from agents.title_writer import TitleCopywriterAgent
from components.workflow_viz import render_workflow_visualization
from components.dialog_history import add_to_dialog_history, update_progress
from utils.state import State


def node_summarize(state: State) -> Generator[State, None, State]:
    """
    要約ノード: テキストの要約を生成する
    """
    client = get_client()
    agent = SummarizerAgent(client)
    
    # SummarizerAgentを呼び出す度に revision_count をインクリメント
    state["revision_count"] += 1
    
    # システムメッセージを対話履歴に追加
    state = add_to_dialog_history(
        state, 
        "system", 
        f"要約エージェントが要約を作成 (第{state['revision_count']}版)",
        progress=10
    )
    
    # ワークフロー図の可視化
    if "current_node" not in state or state["current_node"] != "summarize":
        state["current_node"] = "summarize"
        render_workflow_visualization(state, current_node="summarize")
    
    # 開始メッセージ（進捗バー付き）
    process_message_index = len(state["dialog_history"])
    state = add_to_dialog_history(
        state, 
        "summarizer", 
        "要約を生成します...",
        progress=20
    )
    yield state  # <-- UIを更新
    
    # 進捗更新 (API準備)
    state = update_progress(state, process_message_index, 40)
    yield state  # <-- 進捗更新
    
    # 1回目の要約かどうかで処理を分岐
    if state["revision_count"] == 1:
        summary = agent.call(state["input_text"])
    else:
        summary = agent.refine(state["input_text"], state["feedback"])
    
    # 進捗更新 (API完了)
    state = update_progress(state, process_message_index, 90)
    yield state  # <-- 進捗更新
    
    state["summary"] = summary
    
    # 進捗更新 (完了)
    state = update_progress(state, process_message_index, 100)
    yield state  # <-- 進捗更新
    
    # エージェントの応答をログ
    state = add_to_dialog_history(
        state, 
        "summarizer", 
        f"【要約 第{state['revision_count']}版】\n{summary}"
    )
    yield state  # <-- 増分更新
    
    return state


def node_review(state: State) -> Generator[State, None, State]:
    """
    レビューノード: 要約の品質を評価する
    """
    client = get_client()
    agent = ReviewerAgent(client)
    
    # ワークフロー図の可視化
    if "current_node" not in state or state["current_node"] != "review":
        state["current_node"] = "review"
        render_workflow_visualization(state, current_node="review")
    
    # システムメッセージ
    state = add_to_dialog_history(
        state, 
        "system", 
        f"批評エージェントが要約レビューを実施",
        progress=10
    )
    
    # 開始メッセージ（進捗バー付き）
    process_message_index = len(state["dialog_history"])
    state = add_to_dialog_history(
        state, 
        "reviewer", 
        "レビューを実施しています...",
        progress=20
    )
    yield state  # <-- 増分更新
    
    # 進捗更新 (API準備)
    state = update_progress(state, process_message_index, 40)
    yield state  # <-- 進捗更新
    
    # 最終レビューかどうか
    is_final_review = (state["revision_count"] >= 3)
    
    # レビュー実行
    feedback = agent.call(
        current_summary=state["summary"],
        previous_summary=state.get("previous_summary", ""),
        previous_feedback=state.get("previous_feedback", ""),
        is_final_review=is_final_review
    )
    
    # 進捗更新 (API完了)
    state = update_progress(state, process_message_index, 90)
    yield state  # <-- 進捗更新
    
    state["feedback"] = feedback
    state["previous_summary"] = state["summary"]
    state["previous_feedback"] = feedback
    
    # 進捗更新 (完了)
    state = update_progress(state, process_message_index, 100)
    yield state  # <-- 進捗更新
    
    # フィードバックをログ
    state = add_to_dialog_history(
        state,
        "reviewer",
        f"【フィードバック】\n{feedback}"
    )
    yield state  # <-- 増分更新
    
    # 承認判定
    is_approved = agent.check_approval(feedback, state["revision_count"])
    state["approved"] = is_approved
    
    # 判定結果をログ
    judge_msg = "承認" if is_approved else "改訂が必要"
    state = add_to_dialog_history(
        state,
        "reviewer",
        f"【判定】{judge_msg}"
    )
    yield state  # <-- 増分更新
    
    return state


def node_title(state: State) -> Generator[State, None, State]:
    """
    タイトルノード: タイトルのみを生成する（要約はそのまま使用）
    """
    client = get_client()
    agent = TitleCopywriterAgent(client)
    
    # ワークフロー図の可視化
    if "current_node" not in state or state["current_node"] != "title_node":
        state["current_node"] = "title_node"
        render_workflow_visualization(state, current_node="title_node")
    
    # システムメッセージ
    state = add_to_dialog_history(
        state, 
        "system", 
        "タイトル命名エージェントがタイトルを生成します",
        progress=10
    )
    
    # 開始メッセージ（進捗バー付き）
    process_message_index = len(state["dialog_history"])
    state = add_to_dialog_history(
        state, 
        "title", 
        "タイトルを生成しています...",
        progress=20
    )
    yield state  # <-- 増分更新
    
    # 進捗更新 (API準備)
    state = update_progress(state, process_message_index, 40)
    yield state  # <-- 進捗更新
    
    # タイトル生成
    output = agent.call(state["input_text"], state.get("transcript", []), state["summary"])
    
    # 進捗更新 (API完了)
    state = update_progress(state, process_message_index, 90)
    yield state  # <-- 進捗更新
    
    state["title"] = output.get("title", "")
    state["final_summary"] = output.get("summary", "")
    
    # 進捗更新 (完了)
    state = update_progress(state, process_message_index, 100)
    yield state  # <-- 進捗更新
    
    # タイトル生成結果
    state = add_to_dialog_history(
        state,
        "title",
        f"【生成タイトル】『{state['title']}』"
    )
    yield state  # <-- 増分更新
    
    # 処理完了
    state = add_to_dialog_history(
        state, 
        "system", 
        "すべての処理が完了しました。"
    )
    yield state  # <-- 増分更新
    
    # ワークフロー図の最終表示
    state["current_node"] = "END"
    render_workflow_visualization(state, current_node="END")
    
    return state


def should_revise(state: State) -> str:
    """
    批評に基づいて次のステップを決定する条件分岐関数
    
    Args:
        state: 現在の状態
        
    Returns:
        str: 次のノード名
    """
    # 最大改訂回数を超えている場合は次のステップへ
    if state["revision_count"] >= 3:
        return "title_node"
    
    # 承認されていない場合は要約をやり直す
    if not state.get("approved", False):
        return "summarize"
    
    # 承認された場合はタイトル生成へ進む
    return "title_node"
