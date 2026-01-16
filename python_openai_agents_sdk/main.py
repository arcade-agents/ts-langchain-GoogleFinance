from agents import (Agent, Runner, AgentHooks, Tool, RunContextWrapper,
                    TResponseInputItem,)
from functools import partial
from arcadepy import AsyncArcade
from agents_arcade import get_arcade_tools
from typing import Any
from human_in_the_loop import (UserDeniedToolCall,
                               confirm_tool_usage,
                               auth_tool)

import globals


class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name

    async def on_start(self,
                       context: RunContextWrapper,
                       agent: Agent) -> None:
        self.event_counter += 1
        print(f"### ({self.display_name}) {
              self.event_counter}: Agent {agent.name} started")

    async def on_end(self,
                     context: RunContextWrapper,
                     agent: Agent,
                     output: Any) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {
                # agent.name} ended with output {output}"
                agent.name} ended"
        )

    async def on_handoff(self,
                         context: RunContextWrapper,
                         agent: Agent,
                         source: Agent) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {
                source.name} handed off to {agent.name}"
        )

    async def on_tool_start(self,
                            context: RunContextWrapper,
                            agent: Agent,
                            tool: Tool) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}:"
            f" Agent {agent.name} started tool {tool.name}"
            f" with context: {context.context}"
        )

    async def on_tool_end(self,
                          context: RunContextWrapper,
                          agent: Agent,
                          tool: Tool,
                          result: str) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {
                # agent.name} ended tool {tool.name} with result {result}"
                agent.name} ended tool {tool.name}"
        )


async def main():

    context = {
        "user_id": os.getenv("ARCADE_USER_ID"),
    }

    client = AsyncArcade()

    arcade_tools = await get_arcade_tools(
        client, toolkits=["GoogleFinance"]
    )

    for tool in arcade_tools:
        # - human in the loop
        if tool.name in ENFORCE_HUMAN_CONFIRMATION:
            tool.on_invoke_tool = partial(
                confirm_tool_usage,
                tool_name=tool.name,
                callback=tool.on_invoke_tool,
            )
        # - auth
        await auth_tool(client, tool.name, user_id=context["user_id"])

    agent = Agent(
        name="",
        instructions="# Introduction
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
        model=os.environ["OPENAI_MODEL"],
        tools=arcade_tools,
        hooks=CustomAgentHooks(display_name="")
    )

    # initialize the conversation
    history: list[TResponseInputItem] = []
    # run the loop!
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break
        history.append({"role": "user", "content": prompt})
        try:
            result = await Runner.run(
                starting_agent=agent,
                input=history,
                context=context
            )
            history = result.to_input_list()
            print(result.final_output)
        except UserDeniedToolCall as e:
            history.extend([
                {"role": "assistant",
                 "content": f"Please confirm the call to {e.tool_name}"},
                {"role": "user",
                 "content": "I changed my mind, please don't do it!"},
                {"role": "assistant",
                 "content": f"Sure, I cancelled the call to {e.tool_name}."
                 " What else can I do for you today?"
                 },
            ])
            print(history[-1]["content"])

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())