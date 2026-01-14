# An agent that uses GoogleFinance tools provided to perform any task

## Purpose

# Introduction
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
3. Present the historical stock data, highlighting key trends and insights.

## MCP Servers

The agent uses tools from these Arcade MCP Servers:

- GoogleFinance

## Getting Started

1. Install dependencies:
    ```bash
    bun install
    ```

2. Set your environment variables:

    Copy the `.env.example` file to create a new `.env` file, and fill in the environment variables.
    ```bash
    cp .env.example .env
    ```

3. Run the agent:
    ```bash
    bun run main.ts
    ```