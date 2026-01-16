from arcadepy import AsyncArcade
from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, Session
from google_adk_arcade.tools import get_arcade_tools
from google.genai import types
from human_in_the_loop import auth_tool, confirm_tool_usage

import os

load_dotenv(override=True)


async def main():
    app_name = "my_agent"
    user_id = os.getenv("ARCADE_USER_ID")

    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    client = AsyncArcade()

    agent_tools = await get_arcade_tools(
        client, toolkits=["GoogleFinance"]
    )

    for tool in agent_tools:
        await auth_tool(client, tool_name=tool.name, user_id=user_id)

    agent = Agent(
        model=LiteLlm(model=f"openai/{os.environ["OPENAI_MODEL"]}"),
        name="google_agent",
        instruction="# Introduction
Welcome to the Stock Analysis AI Agent! This agent is designed to help you gather important financial information about stock market performance. Whether you're looking for the latest stock price or historical data, this agent utilizes Google Finance APIs to provide you with accurate and timely information.

# Instructions
1. **User Input**: Begin by asking the user for the stock ticker symbol (e.g., 'AAPL' for Apple) and the exchange identifier (e.g., 'NASDAQ'). 
2. **Choose Action**: Prompt the user to choose between fetching current stock summary information or retrieving historical stock data.
3. **Fetch Data**: Based on the user's choice, use the appropriate tool to fetch the requested data.
4. **Present Results**: Display the results in a clear and informative manner, summarizing key information and insights related to the stock.
5. **Follow-Up**: Ask if the user needs additional information or further analysis.

# Workflows
## Workflow 1: Get Current Stock Summary
1. Request user to provide: 
   - `ticker_symbol`
   - `exchange_identifier`
2. Use the tool: **GoogleFinance_GetStockSummary**
   - Input: `ticker_symbol`, `exchange_identifier`
3. Display the current stock price and movement.

## Workflow 2: Get Historical Stock Data
1. Request user to provide:
   - `ticker_symbol`
   - `exchange_identifier`
   - (Optional) `window` (time period for historical data, e.g., '1 month', '6 months')
2. Use the tool: **GoogleFinance_GetStockHistoricalData**
   - Input: `ticker_symbol`, `exchange_identifier`, `window`
3. Present the historical stock data, highlighting key trends and insights.",
        description="An agent that uses GoogleFinance tools provided to perform any task",
        tools=agent_tools,
        before_tool_callback=[confirm_tool_usage],
    )

    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, state={
            "user_id": user_id,
        }
    )
    runner = Runner(
        app_name=app_name,
        agent=agent,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    async def run_prompt(session: Session, new_message: str):
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=new_message)]
        )
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(f'** {event.author}: {event.content.parts[0].text}')

    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        await run_prompt(session, user_input)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())