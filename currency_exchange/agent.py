import os
from typing import List
from typing_extensions import Annotated

import autogen
from autogen.cache import Cache

from .exchange import exchange_rate, get_available_currencies

def create_currency_agents(llm_config: dict):
    """Create and return the currency exchange agents"""
    chatbot = autogen.AssistantAgent(
        name="chatbot",
        system_message="For currency exchange tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
        llm_config=llm_config,
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        llm_config=llm_config,
    )

    @user_proxy.register_for_execution()
    @chatbot.register_for_llm(description="Currency exchange calculator for any currency pair.")
    def currency_calculator(
        base_amount: Annotated[float, "Amount of currency in base_currency"],
        base_currency: Annotated[str, "Base currency (e.g., USD, EUR, GBP, JPY)"],
        quote_currency: Annotated[str, "Quote currency (e.g., USD, EUR, GBP, JPY)"],
    ) -> str:
        """Calculate currency exchange amount using live exchange rates."""
        try:
            rate = exchange_rate(base_currency, quote_currency)
            quote_amount = round(rate * base_amount, 2)  # Round to 2 decimal places
            rate_display = round(rate, 2)  # Round rate to 2 decimal places
            return f"{base_amount:.2f} {base_currency} = {quote_amount:.2f} {quote_currency} (Rate: 1 {base_currency} = {rate_display:.2f} {quote_currency})"
        except ValueError as e:
            return f"Error: {str(e)}"

    return chatbot, user_proxy

def run_currency_exchange(llm_config: dict, messages: List[str]):
    """Run currency exchange conversations"""
    chatbot, user_proxy = create_currency_agents(llm_config)
    
    with Cache.disk() as cache:
        for message in messages:
            print(f"Query: {message}")
            user_proxy.initiate_chat(
                chatbot,
                message=message,
                summary_method="reflection_with_llm",
                cache=cache
            )
            print("---")
