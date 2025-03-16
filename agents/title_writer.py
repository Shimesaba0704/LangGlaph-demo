import json
from typing import Dict, Any, List
from utils.api_client import DeepseekAPI

class TitleCopywriterAgent:
    """タイトルと最終要約を生成するエージェント"""
    
    def __init__(self, api_client: DeepseekAPI):
        """
        初期化
        
        Args:
            api_client: API呼び出しを行うクライアント
        """
        self.api_client = api_client
        self.prompt_template = (
            "あなたは創造的なタイトルコピーライターです。以下の入力文と、これまでのエージェントの出力を踏まえて、\n"
            "文学作品としてふさわしいタイトルを提案してください。\n"
            "要約自体はすでに完成していますので、タイトルのみを考えてください。\n"
            "【入力文】\n{input_text}\n\n"
            "【これまでの出力】\n{transcript}\n\n"
            "【承認された要約】\n{approved_summary}\n\n"
            "以下のJSON形式で結果を返してください：\n"
            "{{\n"
            "  \"title\": \"提案するタイトル\"\n"
            "}}"
        )

    def call(self, input_text: str, transcript: List[str], approved_summary: str) -> dict:
        """
        タイトルを生成（要約は承認済みのものをそのまま使用）
        
        Args:
            input_text: 原文
            transcript: これまでの対話履歴
            approved_summary: 承認された最終要約
            
        Returns:
            dict: {title: タイトル, summary: 最終要約}の辞書
        """
        transcript_text = "\n".join(transcript)
        prompt = self.prompt_template.format(
            input_text=input_text,
            transcript=transcript_text,
            approved_summary=approved_summary
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "タイトルを生成してください。"}
        ]
        
        try:
            # JSON modeを有効にして呼び出し
            output = self.api_client.invoke(messages, json_mode=True).strip()
            
            # 直接JSONとしてパースを試みる
            try:
                result = json.loads(output)
                # 承認された要約をそのまま使用する
                result["summary"] = approved_summary
                return result
            except json.JSONDecodeError as e:
                # JSONパースに失敗した場合、テキストから抽出を試みる
                print(f"JSONパースエラー: {e}")
                print(f"パースに失敗した出力: {output}")
                
                # コードブロックがある場合は除去
                if "```json" in output:
                    output = output.split("```json")[1].split("```")[0].strip()
                elif "```" in output:
                    output = output.split("```")[1].split("```")[0].strip()
                
                # 余分な説明文がある場合、JSON部分だけを取り出す
                if "{" in output and "}" in output:
                    start_idx = output.find("{")
                    end_idx = output.rfind("}") + 1
                    output = output[start_idx:end_idx]
                
                # 再度JSONパース
                try:
                    result = json.loads(output)
                    # 承認された要約をそのまま使用する
                    result["summary"] = approved_summary
                    return result
                except Exception as e2:
                    print(f"フォールバック処理でもエラー: {e2}")
                    return {
                        "title": "JSONパースエラー",
                        "summary": approved_summary  # エラー時も承認された要約を使用
                    }
        except Exception as e:
            print(f"予期せぬエラー: {e}")
            print(f"問題の出力: {output if 'output' in locals() else 'No output'}")
            return {
                "title": "エラーが発生しました",
                "summary": approved_summary  # エラー時も承認された要約を使用
            }