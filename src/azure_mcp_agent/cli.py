"""CLI entry point for Azure Resource Guide Agent

This module provides an interactive REPL for natural language queries
to Azure resources via Azure MCP Server.
"""

import asyncio
import sys
from typing import Optional

from .agent import create_agent
from .config import get_settings, validate_mcp_server_available
from .prompts import get_error_message


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


async def run_interactive_session():
    """Run an interactive REPL session with the agent"""
    try:
        # Load settings and validate
        settings = get_settings()
        
        # Check if MCP server command is available
        if not validate_mcp_server_available():
            print(f"警告: MCP サーバーコマンド '{settings.mcp_command}' が見つかりません。")
            print(f"Node.js / npm がインストールされていることを確認してください。")
            print()
        
        print("エージェントを初期化しています...")
        agent = await create_agent(settings)
        thread = agent.get_new_thread()
        print("初期化完了！質問を入力してください。")
        print()
        
        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = input("あなた: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', '終了']:
                    print("\nエージェントを終了します。")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process query with agent
                print("\nエージェント: ", end="", flush=True)
                async for chunk in agent.run_stream([user_input], thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print("\n")
                
            except EOFError:
                # Handle Ctrl+D
                print("\n\nエージェントを終了します。")
                break
                
    except ValueError as e:
        # Configuration error
        print(f"設定エラー: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        # MCP connection error
        print(f"接続エラー: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Unexpected error
        print(f"予期しないエラーが発生しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def main():
    """Main CLI entry point"""
    print_banner()
    
    try:
        # Run the interactive session
        exit_code = asyncio.run(run_interactive_session())
        return exit_code
    except KeyboardInterrupt:
        print("\n\n中断されました。エージェントを終了します。")
        return 0
    except Exception as e:
        print(f"\nエラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
