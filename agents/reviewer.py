from typing import Dict, Any
from utils.api_client import DeepseekAPI

class ReviewerAgent:
    """要約の品質を評価するエージェント"""
    
    def __init__(self, api_client: DeepseekAPI):
        """
        初期化
        
        Args:
            api_client: API呼び出しを行うクライアント
        """
        self.api_client = api_client
        self.prompt_template = (
            "あなたは批評家です。（一回目の批評ではない場合には）前回の要約とそれに対するフィードバック、そして今回の要約を示します。\n"
            "前回の要約に対して行った指摘が、今回の要約でどのように修正されているかを確認し、"
            "要約文のクオリティを評価して、必要な修正がまだ残っているかどうか評価してください。\n\n"
            "【前回の要約】\n{previous_summary}\n"
            "【前回のフィードバック】\n{previous_feedback}\n"
            "【今回の要約】\n{current_summary}\n\n"
            "前回の要約および前回のフィードバックがない場合、この批評が一回目の批評になります。\n"
            "一回目の批評の場合は厳しく評価するようにしてください。\n"
            "評価には一貫性を持たせるよう、こころがけて下さい\n"
            "修正が十分であれば承認し、不十分であれば具体的な改善点を提示のうえ再修正が必要と判断してください。"
        )
        
        # 最終回のレビュー用のプロンプト（より肯定的な評価を促す）
        self.final_review_prompt_template = (
            "あなたは批評家です。これは最終の批評機会です。前回の要約とそれに対するフィードバック、そして今回の要約を示します。\n"
            "前回の要約に対して行った指摘が、今回の要約でどのように修正されているかを確認し、"
            "要約文のクオリティを評価してください。\n\n"
            "【前回の要約】\n{previous_summary}\n"
            "【前回のフィードバック】\n{previous_feedback}\n"
            "【今回の要約】\n{current_summary}\n\n"
            "これが最終レビューとなるため、大きな問題がない限りは承認する方向で評価してください。\n"
            "小さな改善点があっても、全体として要約の品質が許容できるレベルであれば、それらを指摘しつつも「承認」としてください。\n"
            "評価には一貫性を持たせるよう、こころがけて下さい。"
        )

    def call(self, current_summary: str, previous_summary: str = "", previous_feedback: str = "", is_final_review: bool = False) -> str:
        """
        要約の品質を評価
        
        Args:
            current_summary: 現在の要約文
            previous_summary: 前回の要約文（存在する場合）
            previous_feedback: 前回のフィードバック（存在する場合）
            is_final_review: 最終レビューかどうか
            
        Returns:
            str: 評価結果
        """
        # 最終レビューの場合は別のプロンプトを使用
        if is_final_review:
            prompt_template = self.final_review_prompt_template
        else:
            prompt_template = self.prompt_template
            
        prompt = prompt_template.format(
            previous_summary=previous_summary or "（最初の要約のため、前回の要約はありません）",
            previous_feedback=previous_feedback or "（最初の要約のため、前回のフィードバックはありません）",
            current_summary=current_summary
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": current_summary}
        ]
        
        try:
            result = self.api_client.invoke(messages)
            return result.strip()
        except Exception as e:
            # エラーログ出力と一般的なエラーメッセージを返す
            print(f"Error in ReviewerAgent.call: {str(e)}")
            return "レビュー中にエラーが発生しました。もう一度お試しください。"
            
    def check_approval(self, feedback: str, revision_count: int = 0, max_revisions: int = 3) -> bool:
        """
        フィードバックから承認状態を判定
        
        Args:
            feedback: 生成されたフィードバック
            revision_count: 現在の改訂回数
            max_revisions: 最大改訂回数
            
        Returns:
            bool: 承認されたかどうか
        """
        # 最大改訂回数に達した場合は強制的に承認とする
        if revision_count >= max_revisions:
            print(f"最大改訂回数({max_revisions}回)に達したため、自動的に承認します。")
            return True
        
        approval_prompt = (
            "以下の批評内容から、この要約が十分な品質であるかを判断してください。"
            "良い要約であれば 'approved' と、改善が必要な要約であれば 'needs_revision' と返してください。\n"
            f"批評内容: {feedback}"
        )
        
        approval_messages = [
            {"role": "system", "content": approval_prompt},
            {"role": "user", "content": "この要約は十分な品質ですか？"}
        ]
        
        try:
            approval_result = self.api_client.invoke(approval_messages).strip().lower()
            return "approved" in approval_result
        except Exception as e:
            # エラー時は安全のため非承認とする
            print(f"Error in ReviewerAgent.check_approval: {str(e)}")
            return False