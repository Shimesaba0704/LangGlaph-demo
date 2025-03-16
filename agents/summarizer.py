from typing import Dict, Any
from utils.api_client import DeepseekAPI

class SummarizerAgent:
    """文章要約を行うエージェント"""
    
    def __init__(self, api_client: DeepseekAPI):
        """
        初期化
        
        Args:
            api_client: API呼び出しを行うクライアント
        """
        self.api_client = api_client
        self.prompt_template = (
            "あなたは優れた要約者です。以下の文章を簡潔に要約してください。\n"
            "【入力】\n{input_text}\n"
            "文章がただの情報ではなく何らかのテーマ性があるものである場合には、そのテーマを見出すよう努めると評価が高まります"
        )
        self.refine_prompt_template = (
            "あなたは優れた要約者です。以下の文章と、批評家からのフィードバックをもとに、要約を改善してください。\n"
            "【入力文章】\n{input_text}\n"
            "【フィードバック】\n{feedback}\n"
            "文章がただの情報ではなく何らかのテーマ性があるものである場合には、そのテーマを見出すよう努めると評価が高まります\n"
            "改善された要約を出力してください。"
        )

    def call(self, input_text: str) -> str:
        """
        文章の要約を生成
        
        Args:
            input_text: 要約する文章
            
        Returns:
            str: 生成された要約
        """
        prompt = self.prompt_template.format(input_text=input_text)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text}
        ]
        
        try:
            result = self.api_client.invoke(messages)
            return result.strip()
        except Exception as e:
            # エラーログ出力と一般的なエラーメッセージを返す
            print(f"Error in SummarizerAgent.call: {str(e)}")
            return "要約の生成中にエラーが発生しました。もう一度お試しください。"

    def refine(self, input_text: str, feedback: str) -> str:
        """
        フィードバックをもとに要約を改善
        
        Args:
            input_text: 原文
            feedback: 批評家からのフィードバック
            
        Returns:
            str: 改善された要約
        """
        prompt = self.refine_prompt_template.format(input_text=input_text, feedback=feedback)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text}
        ]
        
        try:
            result = self.api_client.invoke(messages)
            return result.strip()
        except Exception as e:
            # エラーログ出力と一般的なエラーメッセージを返す
            print(f"Error in SummarizerAgent.refine: {str(e)}")
            return "要約の改善中にエラーが発生しました。もう一度お試しください。"