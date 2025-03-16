import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, Optional


def render_workflow_visualization(state: Dict[str, Any], current_node: Optional[str] = None):
    """レスポンシブ対応したSVGベースのワークフローグラフを描画"""
    
    # ノードの状態マッピング
    nodes = [
        {"id": "start", "name": "開始", "x": 80, "y": 60},
        {"id": "summarize", "name": "要約生成", "x": 260, "y": 60},
        {"id": "review", "name": "レビュー", "x": 440, "y": 60},
        {"id": "title", "name": "タイトル生成", "x": 620, "y": 60},
        {"id": "end", "name": "完了", "x": 800, "y": 60}
    ]
    
    # エッジ定義
    edges = [
        {"source": "start", "target": "summarize", "type": "normal"},
        {"source": "summarize", "target": "review", "type": "normal"},
        {"source": "review", "target": "title", "type": "approval", "label": "承認時"},
        {"source": "review", "target": "summarize", "type": "revision", "label": "改訂要求"},
        {"source": "title", "target": "end", "type": "normal"}
    ]
    
    # ノードマッピング
    node_mapping = {
        "summarize": "summarize",
        "review": "review",
        "title_node": "title",
        "END": "end"
    }
    active_node = node_mapping.get(current_node, "start")
    
    # レスポンシブデザイン対応のHTMLとSVG
    html_code = """
    <div style="background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 0; overflow-x: auto;">
        <style>
            .workflow-container {
                min-width: 800px; /* 最小幅を設定 */
                width: 100%;
                position: relative;
            }
            .workflow-svg {
                width: 100%;
                height: 120px;
                min-width: 800px;
            }
            @media screen and (max-width: 992px) {
                .workflow-container {
                    overflow-x: auto;
                }
            }
            /* その他のスタイル定義 */
            .status-bar {
                display: flex;
                justify-content: space-between;
                margin-top: 5px;
            }
            .status-badge {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
        </style>
        <div class="workflow-container">
            <svg class="workflow-svg" viewBox="0 0 900 120" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <!-- メインノード用グラデーション（青緑系） -->
                    <linearGradient id="main-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#004D40" />
                        <stop offset="100%" stop-color="#00796B" />
                    </linearGradient>
                    
                    <!-- 開始・終了ノード用グラデーション（グレー） -->
                    <linearGradient id="gray-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#455A64" />
                        <stop offset="100%" stop-color="#607D8B" />
                    </linearGradient>
                    
                    <!-- アクティブノード用グラデーション -->
                    <linearGradient id="active-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#00796B" />
                        <stop offset="100%" stop-color="#4DB6AC" />
                    </linearGradient>
                    
                    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                        <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
                    </filter>
                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5"
                        markerWidth="6" markerHeight="6"
                        orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#00796B"/>
                    </marker>
                    <marker id="active-arrow" viewBox="0 0 10 10" refX="5" refY="5"
                        markerWidth="6" markerHeight="6"
                        orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#004D40"/>
                    </marker>
                </defs>
    """
    
    # エッジを描画
    for edge in edges:
        source_node = next((n for n in nodes if n["id"] == edge["source"]), None)
        target_node = next((n for n in nodes if n["id"] == edge["target"]), None)
        
        if source_node and target_node:
            source_x = source_node["x"] + 60
            source_y = source_node["y"]
            target_x = target_node["x"] - 60
            target_y = target_node["y"]
            
            # 改訂要求エッジは曲線で表現
            if edge["type"] == "revision":
                html_code += f"""
                <path d="M {source_x} {source_y} C {source_x+20} {source_y+40}, {target_x-20} {target_y+40}, {target_x} {target_y}"
                    stroke="#00796B" stroke-width="2" fill="none" stroke-dasharray="5,3"
                    marker-end="url(#arrow)"/>
                """
                # ラベルを追加 - 矢印の下側に表示するため、yの値を大きくする
                path_mid_x = (source_x + target_x) / 2
                path_mid_y = source_y + 50  # 矢印の下側に表示するため、Y座標を下げる
                html_code += f"""
                <text x="{path_mid_x}" y="{path_mid_y}" text-anchor="middle" fill="#00796B" font-size="12">{edge.get("label", "")}</text>
                """
            else:
                # 直線エッジ
                is_active = (
                    (active_node == edge["source"]) or
                    (active_node == edge["target"] and edge["type"] != "revision")
                )
                
                stroke_color = "#004D40" if is_active else "#00796B"
                stroke_width = "3" if is_active else "2"
                marker_end = "url(#active-arrow)" if is_active else "url(#arrow)"
                
                html_code += f"""
                <line x1="{source_x}" y1="{source_y}" x2="{target_x}" y2="{target_y}"
                    stroke="{stroke_color}" stroke-width="{stroke_width}" 
                    marker-end="{marker_end}"/>
                """
                
                # 承認時ラベルを追加 - 上部に表示
                if edge.get("label"):
                    label_x = (source_x + target_x) / 2
                    label_y = source_y - 15  # 上部に表示するため、Y座標を上げる
                    
                    # より視認性を高めるための背景を追加
                    html_code += f"""
                    <rect x="{label_x - 25}" y="{label_y - 12}" width="50" height="16" rx="3" ry="3"
                          fill="white" opacity="0.9" />
                    <text x="{label_x}" y="{label_y}" text-anchor="middle" fill="{stroke_color}" font-size="12">{edge.get("label", "")}</text>
                    """
    
    # ノードを描画
    for node in nodes:
        is_active = node["id"] == active_node
        
        # ノードの種類による色分け
        if node["id"] in ["start", "end"]:
            # 開始・終了ノードはグレー
            base_fill = "url(#gray-gradient)"
            base_stroke = "#455A64"
            base_text_color = "white"
        else:
            # メインプロセスノードは青緑系
            base_fill = "url(#gray-gradient)"
            base_stroke = "#004D40"
            base_text_color = "white"
        
        # アクティブノードの強調
        fill = "url(#active-gradient)" if is_active else base_fill
        stroke = "#00ACC1" if is_active else base_stroke
        text_color = "white"  # テキストは常に白で視認性を確保
        filter_effect = 'filter="url(#shadow)"' if is_active else ""
        
        html_code += f"""
        <g class="node" id="{node["id"]}" {filter_effect}>
            <rect x="{node["x"] - 60}" y="{node["y"] - 25}" width="120" height="50" rx="25" ry="25"
                fill="{fill}" stroke="{stroke}" stroke-width="2"/>
            <text x="{node["x"]}" y="{node["y"] + 5}" text-anchor="middle" fill="{text_color}" font-weight="500">{node["name"]}</text>
        </g>
        """
    
    # ステータス表示
    status_text = "承認済" if state.get("approved", False) else "未承認"
    status_color = "#1B5E20" if state.get("approved", False) else "#F57F17"
    
    html_code += f"""
            </svg>
        </div>
        <div class="status-bar">
            <span class="status-badge" style="background-color: {status_color}20; color: {status_color};">状態: {status_text}</span>
            <span class="status-badge" style="background-color: #E0F2F1; color: #004D40;">要約実行回数: {state.get("revision_count", 0)}/3</span>
        </div>
    </div>
    """
    
    # HTMLコンポーネントとして表示
    components.html(html_code, height=190)