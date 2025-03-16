"""
アプリケーション設定
"""

# アプリケーション情報
APP_NAME = "LangGraph Demo"
APP_ICON = "🔄"
APP_DESCRIPTION = "DeepseekとLangGraphを使ったテキスト要約ワークフロー"

# API設定のデフォルト値
DEFAULT_API_ENDPOINT = "https://api.deepseek.com/chat/completions"
DEFAULT_TIMEOUT = 60

# ワークフロー設定
MAX_REVISION_COUNT = 3  # 最大改訂回数

# 例文
EXAMPLE_TEXTS = [
    "例文を選択してください...",
    "人工知能（AI）は、機械学習、深層学習、自然言語処理などの技術を通じて、人間のような知能を模倣するコンピュータシステムです。近年のAI技術の急速な進歩により、自動運転車、医療診断、翻訳サービスなど、様々な分野で革新的なアプリケーションが開発されています。AIの発展は私たちの生活や仕事のあり方を大きく変えつつありますが、同時にプライバシーや雇用への影響など、社会的・倫理的な課題も提起しています。",
    "宇宙探査は人類の好奇心と技術の集大成です。太陽系の惑星や衛星への無人探査機の送付から、国際宇宙ステーションでの有人ミッション、さらには将来の火星有人探査計画まで、私たちは宇宙への理解を深め続けています。これらのミッションから得られる科学的データは、地球外生命の可能性の探索や、宇宙の起源についての理解を深めるのに役立っています。宇宙探査は技術革新を促進し、地球上の課題解決にも応用される新技術の開発につながっています。"
]