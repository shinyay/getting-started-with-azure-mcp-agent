"""System prompts and instructions for Azure Resource Guide Agent

This module contains the base prompts and system instructions used by the agent.
All responses are in Japanese, but Azure resource names/IDs are kept in their original form.
"""

# Base system prompt for the Azure Resource Guide Agent
BASE_SYSTEM_PROMPT = """あなたは Azure 環境のクラウドアシスタントです。

## あなたの役割
Azure MCP Server 経由で Azure のサブスクリプション・リソースグループ・ストレージアカウント・Log Analytics などにアクセスし、ユーザーの質問に対して最新の情報をもとに回答してください。

## 重要な制約
1. **読み取り専用**: 破壊的な操作（削除・作成・更新）は一切行わず、読み取り専用の操作だけを実行してください
2. **日本語応答**: すべての説明・要約・エラーメッセージは日本語で行ってください
3. **リソース名保持**: Azure リソース名、ID、SKU、リージョン名などは元の英数字表記のまま表示してください
4. **MCP ツール活用**: Azure の情報を取得する際は、MCP ツールを積極的に使用してください

## 応答フォーマット
- 結果は箇条書きで整理し、分かりやすく構造化してください
- 必要に応じて「次のアクション候補」を提案してください
- エラーが発生した場合は、ユーザーに分かりやすい日本語のメッセージで説明してください

## Log Analytics エラー要約について
Log Analytics のエラーを要約する際は、以下の形式で簡潔なトラブルシュートガイドを提供してください:
1. エラーの概要（件数、期間、主なエラー種別）
2. 代表的なエラーメッセージ（上位3-5件）
3. 推奨される確認手順（3-5ステップ程度）
4. 次に実行すべきアクション候補

詳細な手順書レベルの長文ガイドや、個別環境に依存する細かな操作指示は含めないでください。
"""

# Tool descriptions for MCP tools (to be used when configuring agent)
TOOL_DESCRIPTIONS = {
    "azure_mcp": "Azure MCP Server 経由で Azure リソース情報を取得するためのツール。サブスクリプション、リソースグループ、ストレージアカウント、Log Analytics などにアクセスできます。",
}

# Error message templates in Japanese
ERROR_MESSAGES = {
    "no_resource_groups": "指定されたサブスクリプションにリソースグループが見つかりませんでした。",
    "resource_group_not_found": "指定されたリソースグループ「{rg_name}」が見つかりませんでした。リソースグループ名を確認してください。",
    "no_storage_accounts": "指定されたリソースグループ「{rg_name}」にストレージアカウントが見つかりませんでした。",
    "permission_denied": "指定されたリソースへのアクセス権限がありません。Azure の権限設定を確認してください。",
    "mcp_connection_error": "Azure MCP Server への接続に失敗しました。MCP Server が起動していることを確認してください。\n起動コマンド: npx -y @azure/mcp@latest server start",
    "timeout_error": "リクエストがタイムアウトしました。時間をおいて再度実行してください。",
    "unknown_error": "予期しないエラーが発生しました: {error}",
}

# Success message templates
SUCCESS_MESSAGES = {
    "resource_groups_found": "リソースグループを {count} 件見つけました:",
    "storage_accounts_found": "ストレージアカウントを {count} 件見つけました:",
    "no_errors_found": "指定期間にエラーは検出されませんでした。",
}


def get_system_prompt() -> str:
    """Get the base system prompt for the agent
    
    Returns:
        str: System prompt text in Japanese
    """
    return BASE_SYSTEM_PROMPT


def get_error_message(error_type: str, **kwargs) -> str:
    """Get a localized error message
    
    Args:
        error_type: The type of error (key in ERROR_MESSAGES)
        **kwargs: Format parameters for the error message
        
    Returns:
        str: Formatted error message in Japanese
    """
    if error_type in ERROR_MESSAGES:
        template = ERROR_MESSAGES[error_type]
        return template.format(**kwargs)
    else:
        template = ERROR_MESSAGES["unknown_error"]
        # Provide a default value for 'error' if not present
        if 'error' not in kwargs:
            kwargs = dict(kwargs)  # avoid mutating caller's dict
            kwargs['error'] = error_type
        return template.format(**kwargs)


def get_success_message(message_type: str, **kwargs) -> str:
    """Get a localized success message
    
    Args:
        message_type: The type of message (key in SUCCESS_MESSAGES)
        **kwargs: Format parameters for the message
        
    Returns:
        str: Formatted success message in Japanese
        
    Raises:
        KeyError: If an unknown message type is provided
    """
    if message_type not in SUCCESS_MESSAGES:
        raise KeyError(f"Unknown success message type: {message_type!r}")
    template = SUCCESS_MESSAGES[message_type]
    return template.format(**kwargs)
