"""Build Agent using Microsoft Agent Framework in Python
# Run this python script
> pip install agent-framework --pre
> python <this-script-path>.py
"""

import asyncio
import os

from agent_framework import ChatAgent, MCPStdioTool, MCPStreamableHTTPTool, ToolProtocol
from agent_framework_azure_ai import AzureAIAgentClient
from agent_framework.openai import OpenAIChatClient
from openai import AsyncOpenAI
from azure.identity.aio import DefaultAzureCredential

# Microsoft Foundry Agent Configuration
ENDPOINT = "https://ai.azure.com/api/eastus2/agents/v1.0/subscriptions/9e3c171a-b6ae-4789-b9af-e62a63848a06/resourceGroups/rg-syanagihara-250914/providers/Microsoft.MachineLearningServices/workspaces/syanagihara-250914"
MODEL_DEPLOYMENT_NAME = "gpt-4o-250914-hub"

AGENT_NAME = "mcp-agent"
AGENT_INSTRUCTIONS = "あなたは Azure 環境のクラウドアシスタントです。\nAzure MCP Server 経由で Azure のサブスクリプション・リソースグループ・ストレージアカウントなどを確認できます。\nMCP ツールを積極的に使って、ユーザーの質問に対して 最新の情報をもとに回答してください。\n破壊的な操作（削除・作成）は行わず、読み取り専用の操作だけを実行してください。\n応答は日本語で行い、リソース名やIDなどは原文を維持してください。\n結果は箇条書きで整理し、必要に応じて「次のアクション候補」を提案してください。"

# User inputs for the conversation
USER_INPUTS = [
    "このサブスクリプションで利用可能なサブスクリプション一覧を出して",
    "このサブスクリプションで利用可能なサブスクリプション一覧を出して",
    "利用中のリソースグループを一覧して、名前とリージョンを教えて",
    "このサブスクリプションで利用可能なサブスクリプション一覧を出して",
    "利用中のリソースグループを一覧して、名前とリージョンを教えて",
]

def create_mcp_tools() -> list[ToolProtocol]:
    return [
        MCPStdioTool(
            name="VSCode Tools".replace("-", "_"),
            description="MCP server for VSCode Tools",
            command="INSERT_COMMAND_HERE",
            args=[
                "INSERT_ARGUMENTS_HERE",
            ]
        ),
    ]

async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(
                project_endpoint=ENDPOINT,
                model_deployment_name=MODEL_DEPLOYMENT_NAME,
                async_credential=credential,
                agent_name=AGENT_NAME,
                agent_id=None,  # Since no Agent ID is provided, the agent will be automatically created and deleted after getting response
            ),
            instructions=AGENT_INSTRUCTIONS,
            max_completion_tokens=4096,
            tools=[
                *create_mcp_tools(),
            ],
        ) as agent
    ):
        # Create a new thread that will be reused
        thread = agent.get_new_thread()

        # Process user messages
        for user_input in USER_INPUTS:
            print(f"\n# User: '{user_input}'")
            async for chunk in agent.run_stream([user_input], thread=thread):
                if chunk.text:
                    print(chunk.text, end="")
                elif (
                    chunk.raw_representation
                    and chunk.raw_representation.raw_representation
                    and hasattr(chunk.raw_representation.raw_representation, "status")
                    and hasattr(chunk.raw_representation.raw_representation, "type")
                    and chunk.raw_representation.raw_representation.status == "completed"
                    and hasattr(chunk.raw_representation.raw_representation, "step_details")
                    and hasattr(chunk.raw_representation.raw_representation.step_details, "tool_calls")
                ):
                    print("")
                    print("Tool calls: ", chunk.raw_representation.raw_representation.step_details.tool_calls)
            print("")

        print("\n--- All tasks completed successfully ---")

    # Give additional time for all async cleanup to complete
    await asyncio.sleep(1.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Program finished.")
