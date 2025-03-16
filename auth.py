import streamlit as st
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

def check_password():
    """
    ユーザー認証を処理する関数
    
    Returns:
        bool: 認証成功の場合True、それ以外の場合False
    """
    # 環境変数から認証情報を取得
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "password")
    
    # 複数ユーザー対応 (カンマ区切りで複数のユーザー名:パスワードを設定可能)
    user_credentials = os.getenv("USER_CREDENTIALS", "")
    
    # 認証状態の管理
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if st.session_state.authenticated:
        return True
        
    # ログアウト処理
    if "logout" in st.query_params:
        st.session_state.authenticated = False
        # クエリパラメータをクリア
        st.query_params.clear()
        
    # 既に認証済みの場合はスキップ
    if st.session_state.authenticated:
        return True
    
    # ログインフォームの表示
    st.markdown("""
    <div style="text-align: center; margin: 30px auto; padding: 0 20px;">
        <img src="https://langchain-ai.github.io/langgraph/static/wordmark_dark.svg" 
            alt="LangGraph" 
            style="width: 80%; max-width: 250px; display: block; margin: 0 auto;">
        <h2 style="margin-top: 30px; color: #00796B;">ログイン</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # カードスタイルのフォーム
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # ログインフォーム
    username = st.text_input("ユーザー名", key="username_input")
    password = st.text_input("パスワード", type="password", key="password_input")
    
    # 認証ボタン
    if st.button("ログイン", use_container_width=True, key="login_button"):
        # 管理者アカウントとのチェック
        if username == admin_username and password == admin_password:
            st.session_state.authenticated = True
            st.rerun()
            return True
            
        # 追加のユーザー認証情報をチェック
        if user_credentials:
            credentials_list = user_credentials.split(',')
            for credential in credentials_list:
                if ':' in credential:
                    user, pwd = credential.strip().split(':')
                    if username == user and password == pwd:
                        st.session_state.authenticated = True
                        st.rerun()
                        return True
        
        st.error("ユーザー名またはパスワードが正しくありません。")
        return False
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 認証に失敗または初回アクセス時
    return False

def auth_required(func):
    """
    認証を要求するデコレータ関数
    
    Args:
        func: 保護対象の関数
    """
    def wrapper(*args, **kwargs):
        if check_password():
            # ログアウトボタンを上部右側に表示
            col1, col2 = st.columns([6, 1])
            with col2:
                if st.button("ログアウト", key="logout_button"):
                    # ログアウト用のクエリパラメータを追加してページをリロード
                    st.query_params["logout"] = "true"
                    return
            
            # 認証が成功した場合、元の関数を実行
            return func(*args, **kwargs)
        
    return wrapper