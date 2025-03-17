import streamlit as st
from typing import Dict, Any, Generator
from utils.api_client import get_client
from agents.summarizer import SummarizerAgent
from agents.reviewer import ReviewerAgent
from agents.title_writer import TitleCopywriterAgent
from components.workflow_viz import render_workflow_visualization
from components.dialog_history import add_to_dialog_history
from utils.state import State


def node_summarize(state: State) -> Generator[State, None, State]:
    """
    要約ノード: テキストの要約を生成する
    """
    client = get_client()
    agent = SummarizerAgent(client)
    
    # SummarizerAgentを呼び出す度に revision_count をインクリメント
    state["revision_count"] += 1
    
    # ワークフロー図の可視化
    if "current_node" not in state or state["current_node"] != "summarize":
        state["current_node"] = "summarize"
        # render_workflow_visualization はUI更新するためスレッドから直接呼ばない
        # 代わりに状態を返して、メインスレッドでUI更新する
    
    # システムメッセージを対話履歴に追加
    state = add_to_dialog_history(
        state, 
        "system", 
        f"要約エージェントが要約を作成 (第{state['revision_count']}版)",
        progress=10  # 進捗状況の追加（10%）
    )
    
    # 開始メッセージ
    state = add_to_dialog_history(
        state, 
        "summarizer", 
        "要約を生成しています...",
        progress=20  # 進捗状況の追加（20%）
    )
    # 状態を返してUIを更新
    yield state
    
    # 1回目の要約かどうかで処理を分岐
    state = add_to_dialog_history(
        state, 
        "summarizer", 
        "テキストを分析中...",
        progress=30  # 進捗状況の追加（30%）
    )
    yield state
    
    try:
        if state["revision_count"] == 1:
            state = add_to_dialog_history(
                state, 
                "summarizer", 
                "初回の要約を作成中...",
                progress=40  # 進捗状況の追加（40%）
            )
            yield state
            summary = agent.call(state["input_text"])
        else:
            state = add_to_dialog_history(
                state, 
                "summarizer", 
                f"フィードバックを基に要約を改善中...",
                progress=40  # 進捗状況の追加（40%）
            )
            yield state
            summary = agent.refine(state["input_text"], state["feedback"])
        
        state["summary"] = summary
        
        # エージェントの応答をログ
        state = add_to_dialog_history(
            state, 
            "summarizer", 
            f"【要約 第{state['revision_count']}版】\n{summary}",
            progress=60  # 進捗状況の追加（60%）
        )
    except Exception as e:
        # エラーハンドリング
        error_message = f"要約生成中にエラーが発生しました: {str(e)}"
        state = add_to_dialog_history(
            state,
            "system",
            error_message,
            progress=30  # エラー時は進捗を進めない
        )
        state["error"] = error_message
    
    # 状態を返してUIを更新
    yield state
    
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
        # レンダリングはメインスレッドで行う
    
    # システムメッセージ
    state = add_to_dialog_history(
        state, 
        "system", 
        f"批評エージェントが要約レビューを実施",
        progress=65  # 進捗状況の追加（65%）
    )
    
    # 開始メッセージ
    state = add_to_dialog_history(
        state, 
        "reviewer", 
        "レビューを実施しています...",
        progress=70  # 進捗状況の追加（70%）
    )
    # 状態を返してUIを更新
    yield state
    
    # レビュー進行中メッセージ
    state = add_to_dialog_history(
        state, 
        "reviewer", 
        "要約の品質を評価中...",
        progress=75  # 進捗状況の追加（75%）
    )
    yield state
    
    try:
        # 最終レビューかどうか
        is_final_review = (state["revision_count"] >= 3)
        
        # レビュー実行
        feedback = agent.call(
            current_summary=state["summary"],
            previous_summary=state.get("previous_summary", ""),
            previous_feedback=state.get("previous_feedback", ""),
            is_final_review=is_final_review
        )
        
        state["feedback"] = feedback
        state["previous_summary"] = state["summary"]
        state["previous_feedback"] = feedback
        
        # フィードバックをログ
        state = add_to_dialog_history(
            state,
            "reviewer",
            f"【フィードバック】\n{feedback}",
            progress=80  # 進捗状況の追加（80%）
        )
        
        # 承認判定
        is_approved = agent.check_approval(feedback, state["revision_count"])
        state["approved"] = is_approved
        
        # 判定結果をログ
        judge_msg = "承認" if is_approved else "改訂が必要"
        state = add_to_dialog_history(
            state,
            "reviewer",
            f"【判定】{judge_msg}",
            progress=85  # 進捗状況の追加（85%）
        )
    except Exception as e:
        # エラーハンドリング
        error_message = f"レビュー中にエラーが発生しました: {str(e)}"
        state = add_to_dialog_history(
            state,
            "system",
            error_message,
            progress=70  # エラー時は進捗を進めない
        )
        state["error"] = error_message
        # エラー時はデフォルトで承認として扱い、次のステップに進める
        state["approved"] = True
    
    # 状態を返してUIを更新
    yield state
    
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
        # レンダリングはメインスレッドで行う
    
    # システムメッセージ
    state = add_to_dialog_history(
        state, 
        "system", 
        "タイトル命名エージェントがタイトルを生成します",
        progress=87  # 進捗状況の追加（87%）
    )
    
    # 開始メッセージ
    state = add_to_dialog_history(
        state, 
        "title", 
        "タイトルを生成しています...",
        progress=90  # 進捗状況の追加（90%）
    )
    # 状態を返してUIを更新
    yield state
    
    # 進捗メッセージ追加
    state = add_to_dialog_history(
        state, 
        "title", 
        "要約内容からタイトルを検討中...",
        progress=93  # 進捗状況の追加（93%）
    )
    yield state
    
    try:
        # タイトル生成
        output = agent.call(state["input_text"], state.get("transcript", []), state["summary"])
        
        state["title"] = output.get("title", "")
        state["final_summary"] = output.get("summary", "")
        
        # タイトル生成結果
        state = add_to_dialog_history(
            state,
            "title",
            f"【生成タイトル】『{state['title']}』",
            progress=96  # 進捗状況の追加（96%）
        )
        
        # 処理完了
        state = add_to_dialog_history(
            state, 
            "system", 
            "すべての処理が完了しました。",
            progress=100  # 進捗状況の追加（100%）
        )
    except Exception as e:
        # エラーハンドリング
        error_message = f"タイトル生成中にエラーが発生しました: {str(e)}"
        state = add_to_dialog_history(
            state,
            "system",
            error_message,
            progress=90  # エラー時は進捗を進めない
        )
        state["error"] = error_message
        # エラー時もタイトルとサマリーをデフォルト値で設定
        state["title"] = "エラーが発生しました"
        state["final_summary"] = state.get("summary", "要約が生成できませんでした。")
        
        # エラー完了メッセージ
        state = add_to_dialog_history(
            state, 
            "system", 
            "エラーが発生しましたが、処理を完了します。",
            progress=100  # エラー時も完了として扱う
        )
    
    # 状態を返してUIを更新
    yield state
    
    # 完了状態に移行
    state["current_node"] = "END"
    # レンダリングはメインスレッドで行うため、ここでは状態設定のみを行う
    
    return state


def should_revise(state: State) -> str:
    """
    批評に基づいて次のステップを決定する条件分岐関数
    
    Args:
        state: 現在の状態
        
    Returns:
        str: 次のノード名
    """
    # エラーが発生した場合は直接タイトル生成へ進む
    if "error" in state:
        return "title_node"
        
    # 最大改訂回数を超えている場合は次のステップへ
    if state["revision_count"] >= 3:
        return "title_node"
    
    # 承認されていない場合は要約をやり直す
    if not state.get("approved", False):
        return "summarize"
    
    # 承認された場合はタイトル生成へ進む
    return "title_node"
