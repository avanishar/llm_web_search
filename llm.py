import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def call_gemini(prompt):
    """
    Call Gemini API with a given prompt and print token usage.
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    # Token usage metadata
    usage = response.usage_metadata
    print("\033[96m" + f"📊 Model: gemini-2.5-flash | "
          f"Input tokens: {usage.prompt_token_count} | "
          f"Output tokens: {usage.candidates_token_count} | "
          f"Total tokens: {usage.total_token_count}" + "\033[0m")
    print("-" * 50)

    return response.text


def context_combine_prompt(context_from_logs, topic):
    """
    Combine scraped context with the question to form a final prompt.
    """
    return (
        "Take this context: " + context_from_logs +
        "\n\nNow answer this question strictly based on the context. "
        "Do NOT make anything up yourself.\n\n"
        "Q: " + topic
    )
