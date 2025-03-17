import streamlit as st

def apply_theme_styles():
    """
    アプリケーション全体のUIスタイルを設定
    """
    # CSS
    st.markdown("""
    <style>
    /* カラー変数 */
    :root {
        --primary: #004D40;
        --secondary: #00796B;
        --light: #E0F2F1;
        --accent: #4DB6AC;
        --background: #f8f9fa;
        --card-bg: #ffffff;
        --text: #333333;
    }
    
    /* 全体のデザイン */
    .main {
        background-color: var(--background);
        color: var(--text);
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* サイドバーのスタイル */
    [data-testid="stSidebar"] {
        background-color: var(--primary);
        color: white !important;
        padding: 1rem;
    }

    /* サイドバー内のテキスト */
    [data-testid="stSidebar"] .css-pkbazv {
        color: white !important;
    }
    
    /* ヘッダーとタイトル */
    h1 {
        color: var(--primary);
        font-family: 'Segoe UI', sans-serif;
        font-size: 2.2rem;
        font-weight: 600;
        border-bottom: 2px solid var(--secondary);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    h2 {
        color: var(--secondary);
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.8rem;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    h3 {
        color: var(--secondary);
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.4rem;
        margin-top: 0.75rem;
        margin-bottom: 0.5rem;
    }
    
    /* コンパクトなカードコンポーネント */
    .card {
        background-color: var(--card-bg);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        padding: 1.25rem;
        margin-bottom: 1.25rem;
    }
    
    /* ボタンスタイル */
    .stButton > button {
        background-color: var(--secondary);
        color: white;
        font-weight: 500;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        border: none;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: var(--primary);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 77, 64, 0.2);
    }
    
    /* ワークフロー可視化用 */
    .workflow-container {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* エージェント対話履歴スタイル */
    .agent-output {
        border-left: 3px solid var(--secondary);
        padding: 0.75rem 0.75rem 0.75rem 1.25rem;
        background-color: #f8f9fa;
        border-radius: 0 6px 6px 0;
        margin: 0.75rem 0;
    }
    
    .agent-summarizer {
        border-left-color: #009688;
    }
    
    .agent-reviewer {
        border-left-color: #673AB7;
    }
    
    .agent-title {
        border-left-color: #FF5722;
    }
    
    /* 対話履歴コンテナ */
    .dialog-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 8px;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.25rem;
    }
    
    /* ステータスバッジ */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-blue {
        background-color: var(--light);
        color: var(--primary);
    }
    
    .badge-green {
        background-color: #E8F5E9;
        color: #1B5E20;
    }
    
    .badge-yellow {
        background-color: #FFF8E1;
        color: #F57F17;
    }
    
    .badge-red {
        background-color: #FFEBEE;
        color: #B71C1C;
    }
    
    /* テキストエリアのスタイル */
    .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 1rem;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--secondary);
        box-shadow: 0 0 0 2px rgba(0, 121, 107, 0.2);
    }
    
    /* タブスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3.5rem;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        color: #666;
        font-size: 1rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        color: var(--primary);
        font-weight: bold;
    }
    
    /* セクション間の余白 */
    .section {
        margin-bottom: 1.5rem;
    }
    
    /* 結果カード */
    .result-card {
        border-left: 4px solid var(--secondary);
        background-color: white;
        padding: 1.25rem;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    /* コンテナパディングの調整 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* エクスパンダーの調整 */
    .streamlit-expanderHeader {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* フォーム要素周りの余白削減 */
    div.stButton {
        margin-top: 0.5rem;
    }
    
    /* ワークフロー図のスタイリング */
    .workflow-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.5rem;
    }
    
    /* エージェント別アイコン */
    .agent-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    
    .agent-name {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* 対話履歴コンテナのタイムライン風デザイン */
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
        background-color: var(--secondary);
    }
    
    .timeline-content {
        padding: 0.75rem;
        border-radius: 8px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
                
    .stSelectbox label p {
        color: white !important;
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
    /* アニメーション関連のスタイルも追加 */
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
