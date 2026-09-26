"""Exercise1 - User request extraction to structured output

This module contains the function `extract_request` which takes a message text as input and extracts the structured information about the requested vacation using a language model. 
The structured output is defined by the `RequestVacationInfo` Pydantic model, which includes fields for destination, start date, end date, people count, budget and any missing information. 
The function uses a prompt template to guide the language model in extracting the relevant information from the message text. 
"""
import json
import os
from datetime import date

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from schema import RequestVacationInfo

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")

def extract_request(message_text: str) -> RequestVacationInfo:
    """Extract structured information from a user's vacation request message.

    Args:
        message_text (str): The user's message text containing the vacation request.

    Returns:
        RequestVacationInfo: A Pydantic model containing the extracted structured information.
    """

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant that extracts structured information from user messages."),
            (
                "user",
                "Extract the following structured information from the user's message:\n"
                "- destination (city, region, or country)\n"
                "- start_date (YYYY-MM-DD)\n"
                "- end_date (YYYY-MM-DD)\n"
                "- people_count (number of people traveling)\n"
                "- budget (total budget for the vacation)\n"
                "- missing_info (list of any fields that could not be determined)\n\n"
                "If any information is missing, indicate it in the 'missing_info' field.\n\n"
                "User's message: {message_text}",
            ),
        ]
    )

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL)
    chain = prompt_template | llm.with_structured_output(RequestVacationInfo)

    return chain.invoke({"message_text": message_text})


def _run_test_scenarios() -> None:
    test_messages = {
            "Complete request": (
                "I want to go to Rome from 2026-10-10 to 2026-10-17 with my wife, "
                "we have a budget of 2000 euros."
            ),
            "Missing budget": (
                "We are 4 friends and want to visit Barcelona between 5 and 12 November 2026."
            ),
            "Informal destination": (
                "Me and my family (5 people) want to go somewhere in the Greek islands, "
                "the one with the white houses and blue domes, from 1 to 8 July 2027. "
                "Budget around 5000 euros."
            ),
        }
    
    for name, message in test_messages.items():
            print(f"=== {name} ===")
            print(f"Message: {message}")
            result = extract_request(message)
            print(json.dumps(result.model_dump(mode="json"), indent=2))
            print()

if __name__ == "__main__":
    _run_test_scenarios()