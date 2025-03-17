import streamlit as st
from utils.api_client import get_available_models, update_model, get_selected_model, test_api_connection

def render_sidebar():
    """サイドバーUI - シンプル化"""
    st.sidebar.markdown('<h2 style="color: white;">モデル設定</h2>', unsafe_allow_html=True)
    
    # Deepseekロゴをシンプルに表示
    st.sidebar.markdown("""
    <div style="text-align: center; margin: 1.5rem 0;">
        <img src="https://cdn.deepseek.com/logo.png" width="160" alt="Deepseek Logo" style="filter: brightness(1.2);">
    </div>
    """, unsafe_allow_html=True)
    
    # モデル選択用のセレクトボックス
    available_models = get_available_models()
    selected_model = get_selected_model()
    
    new_selected_model = st.sidebar.selectbox(
        "使用するモデル",
        options=list(available_models.keys()),
        format_func=lambda x: available_models[x],
        index=list(available_models.keys()).index(selected_model) if selected_model in available_models else 0
    )
    
    # モデルが変更された場合、APIクライアントを更新
    if new_selected_model != selected_model:
        update_model(new_selected_model)
    
    st.sidebar.markdown(f"""
    <div style="margin: 1rem 0; padding: 0.75rem; border-radius: 6px; background-color: rgba(255,255,255,0.1);">
        <strong>選択中:</strong> {available_models[new_selected_model]}
    </div>
    """, unsafe_allow_html=True)
    
    # API接続テスト
    if st.sidebar.button("API接続テスト", key="api_test"):
        with st.sidebar:
            with st.spinner("接続テスト実行中..."):
                success, response = test_api_connection()
                if success:
                    st.success(f"✅ API接続成功: {response[:50]}...")
                else:
                    st.error(f"❌ API接続エラー: {response}")
    
    # エージェント情報
    with st.sidebar.expander("ワークフローエージェント", expanded=False):
        st.markdown("""
        - **要約者**: テキストの要約を生成
        - **批評家**: 要約の品質を評価
        - **タイトル作成者**: タイトルと最終要約を生成
        """)
