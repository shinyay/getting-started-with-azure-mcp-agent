"""CLI entry point for Azure Resource Guide Agent

This module provides an interactive REPL for natural language queries
to Azure resources via Azure MCP Server.
"""

import asyncio
import logging
import os
import sys

from .agent import create_agent
from .config import get_settings, validate_mcp_server_available

# Configure logger for this module
logger = logging.getLogger(__name__)


def print_banner():
    """Print the welcome banner"""
    print("=" * 70)
    print("Azure Resource Guide Agent CLI")
    print("=" * 70)
    print()
    print("Azure MCP Server 経由で Azure リソースを日本語で調査できるエージェントです。")
    print()
    print("使い方:")
    print("  - 日本語で質問を入力してください")
    print("  - 'exit' または 'quit' で終了します")
    print("  - Ctrl+C でも終了できます")
    print()
    print("例:")
    print("  - このサブスクリプションのリソースグループ一覧を出して")
    print("  - <RG名> のストレージアカウントを一覧して")
    print("  - 直近1時間のエラーをLog Analyticsで確認して")
    print()
    print("=" * 70)
    print()


async def run_interactive_session() -> int:
    """Run an interactive REPL session with the agent"""
    try:
        # Load settings and validate
        logger.info("設定を読み込んでいます")
        settings = get_settings()
        
        # Check if MCP server command is available
        if not validate_mcp_server_available(settings):
            logger.warning(f"MCP サーバーコマンド '{settings.mcp_command}' が見つかりません")
            print(f"警告: MCP サーバーコマンド '{settings.mcp_command}' が見つかりません。")
            print(f"Node.js / npm がインストールされていることを確認してください。")
            print()
        
        print("エージェントを初期化しています...")
        logger.info("エージェントの作成を開始します")
        agent = await create_agent(settings)
        thread = agent.get_new_thread()
        print("初期化完了！質問を入力してください。")
        print()
        logger.info("対話セッションを開始しました")
        
        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = input("あなた: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', '終了']:
                    logger.info("ユーザーが終了コマンドを入力しました")
                    print("\nエージェントを終了します。")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process query with agent
                logger.info(f"クエリを処理しています (長さ: {len(user_input)} 文字)")
                logger.debug(f"クエリ内容: {user_input[:100]}...")  # 最初の100文字のみログ
                
                print("\nエージェント: ", end="", flush=True)
                response_length = 0
                async for chunk in agent.run_stream([user_input], thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                        response_length += len(chunk.text)
                print("\n")
                
                logger.info(f"クエリ処理が完了しました (応答長: {response_length} 文字)")
                
            except EOFError:
                # Handle Ctrl+D
                logger.info("EOFError を検知しました (Ctrl+D)")
                print("\n\nエージェントを終了します。")
                break
            except Exception as e:
                # Handle errors during query processing
                logger.error(f"クエリ処理中のエラー: {e}", exc_info=True)
                print(f"\nエラーが発生しました: 申し訳ございませんが、この問い合わせの処理中に問題が発生しました。", file=sys.stderr)
                print("別の問い合わせをお試しいただくか、'exit' で終了してください。\n")
                # Continue the loop instead of crashing
                continue
                
    except ValueError as e:
        # Configuration error
        logger.error(f"設定エラー: {e}")
        print(f"設定エラー: {e}", file=sys.stderr)
        print("\n必須の環境変数が設定されていることを確認してください:", file=sys.stderr)
        print("  - GITHUB_MODEL_NAME または AZURE_OPENAI_MODEL_NAME", file=sys.stderr)
        print("  - GITHUB_API_KEY または AZURE_OPENAI_API_KEY", file=sys.stderr)
        return 1
    except RuntimeError as e:
        # MCP connection error
        logger.error(f"接続エラー: {e}")
        print(f"接続エラー: {e}", file=sys.stderr)
        print("\n以下を確認してください:", file=sys.stderr)
        print("  1. Azure MCP Server が起動していること", file=sys.stderr)
        print("  2. Azure 認証が完了していること (az login)", file=sys.stderr)
        print("  3. ネットワーク接続が正常であること", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("KeyboardInterrupt を検知しました")
        print("\n\n中断されました。エージェントを終了します。")
        return 0
    except Exception as e:
        # Unexpected error - don't show stack trace to user
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        print(f"予期しないエラーが発生しました。", file=sys.stderr)
        print("問題が続く場合は、ログファイルを確認してください。", file=sys.stderr)
        return 1
    
    return 0


def _setup_logging():
    """Setup logging configuration for the application"""
    # Get log level from environment variable, default to INFO
    log_level_str = os.environ.get("AZURE_MCP_AGENT_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)  # Log to stderr to avoid mixing with agent output
        ]
    )
    
    # Set log level for our modules
    logging.getLogger('azure_mcp_agent').setLevel(log_level)
    
    # Reduce noise from third-party libraries
    logging.getLogger('agent_framework').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)


def main() -> int:
    """Main CLI entry point"""
    # Setup logging first
    _setup_logging()
    
    logger.info("Azure Resource Guide Agent CLI を起動しています")
    
    print_banner()
    
    try:
        # Run the interactive session
        exit_code = asyncio.run(run_interactive_session())
        logger.info(f"CLI が終了しました (exit code: {exit_code})")
        return exit_code
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt により終了します")
        print("\n\n中断されました。エージェントを終了します。")
        return 0
    except Exception as e:
        logger.error(f"main() での予期しないエラー: {e}", exc_info=True)
        print(f"\nエラー: 予期しないエラーが発生しました。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
