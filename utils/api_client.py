import os
import requests
import json
import streamlit as st
from urllib3.exceptions import InsecureRequestWarning
import urllib3
from dotenv import load_dotenv
load_dotenv()
urllib3.disable_warnings(InsecureRequestWarning)

# 利用可能なモデル一覧
AVAILABLE_MODELS = {
    "deepseek-chat": "Deepseek V3",
    "deepseek-reasoner": "Deepseek R1"
}

class DeepseekAPI:
    """DeepseekのAPI呼び出しを処理するクラス"""
    
    def __init__(self, api_key, endpoint, model, timeout=60):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def invoke(self, messages, json_mode=False):
        """メッセージを送信してレスポンスを取得
        
        Args:
            messages: 会話メッセージの配列
            json_mode: JSONフォーマットのレスポンスを要求する場合はTrue
        """
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        # JSON出力モードを設定
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                verify=False,  # 開発環境のみ
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"APIエラー: ステータスコード {response.status_code}, レスポンス: {response.text}"
                raise Exception(error_msg)
                
        except Exception as e:
            raise Exception(f"API呼び出しエラー: {str(e)}")


def initialize_client():
    """APIクライアントを初期化して session_state に保存"""
    
    if 'api_client' not in st.session_state:
        try:
            # 環境変数からAPIキーを取得
            api_key = os.getenv("DEEPSEEK_API_KEY")
            
            # 環境変数がない場合はエラーメッセージを表示
            if not api_key:
                st.sidebar.error("⚠️ DEEPSEEK_API_KEYが設定されていません。Streamlit Cloud設定で環境変数を設定してください。")
                return
            
            # API エンドポイント
            api_endpoint = os.getenv("API_ENDPOINT", "https://api.deepseek.com/chat/completions")
            
            # デフォルトモデルを設定
            default_model = list(AVAILABLE_MODELS.keys())[0]
            
            # APIクライアントを初期化
            st.session_state.api_client = DeepseekAPI(
                api_key=api_key,
                endpoint=api_endpoint,
                model=default_model,
                timeout=60
            )
            
            st.session_state.selected_model = default_model
            
        except Exception as e:
            st.sidebar.error(f"❌ API接続エラー: {str(e)}")
            
            st.session_state.selected_model = default_model
            
        except Exception as e:
            st.sidebar.error(f"❌ API接続エラー: {str(e)}")
            if "APIエラー" in str(e):
                st.sidebar.warning(f"API呼び出しでエラーが発生しました。詳細: {str(e)}")
            else:
                st.sidebar.warning("予期せぬエラーが発生しました。詳細はログを確認してください。")
            raise e


def update_model(model_name):
    """使用するモデルを更新"""
    if 'api_client' in st.session_state:
        st.session_state.api_client.model = model_name
        st.session_state.selected_model = model_name
        return True
    return False


def get_client():
    """現在のAPIクライアントを取得"""
    if 'api_client' not in st.session_state:
        initialize_client()
    return st.session_state.api_client


def get_available_models():
    """利用可能なモデルのリストを取得"""
    return AVAILABLE_MODELS


def get_selected_model():
    """現在選択されているモデルを取得"""
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = list(AVAILABLE_MODELS.keys())[0]
    return st.session_state.selected_model


def test_api_connection():
    """API接続をテストする"""
    client = get_client()
    try:
        test_message = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "こんにちは、簡単な返事を返してください"}
        ]
        test_response = client.invoke(test_message)
        return True, test_response
    except Exception as e:
        return False, str(e)