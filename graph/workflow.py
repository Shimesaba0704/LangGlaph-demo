from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from utils.state import State
from graph.nodes import node_summarize, node_review, node_title, should_revise


def create_workflow_graph():
    """
    ワークフローグラフを作成
    
    Returns:
        compiled_graph: コンパイル済みのグラフオブジェクト
    """
    # グラフビルダーの初期化
    builder = StateGraph(State)
    
    # ノードの追加
    builder.add_node("summarize", node_summarize)
    builder.add_node("review", node_review)
    builder.add_node("title_node", node_title)
    
    # エッジの定義
    builder.add_edge(START, "summarize")
    builder.add_edge("summarize", "review")
    
    # 条件分岐のエッジを追加
    builder.add_conditional_edges(
        "review",
        should_revise,
        {
            "summarize": "summarize",  # 要約の改訂が必要な場合
            "title_node": "title_node"  # 要約が承認された場合
        }
    )
    
    # 最後のノードから終了へのエッジ
    builder.add_edge("title_node", END)
    
    # チェックポイント設定とグラフのコンパイル
    memory = MemorySaver()
    compiled_graph = builder.compile(checkpointer=memory)
    
    return compiled_graph