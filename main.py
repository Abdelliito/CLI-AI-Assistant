"""
CLI AI Assistant
A tiny command-line chatbot that talks to Google's Gemini API.

Flow: read input -> send to Gemini -> print reply -> repeat until exit.
"""

import os
import sys

from dotenv import load_dotenv    # loads variables from the .env file
from google import genai          # official Google Gen AI SDK
from google.genai import errors   # error classes raised by the SDK

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
# A fast, low-cost "Flash" model, well suited to simple text chat.
# If your key says this model isn't found, try "gemini-2.5-flash".
MODEL = "gemini-3.5-flash"

EXIT_COMMANDS = {"exit", "quit"}
LINE = "=" * 40


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
def create_client() -> genai.Client:
    """Read the API key from .env and create the Gemini client."""
    load_dotenv()  # copies values from .env into environment variables
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        print("Error: GEMINI_API_KEY is missing.")
        print("Open the .env file and set:  GEMINI_API_KEY=your_real_key")
        sys.exit(1)

    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Talking to Gemini
# ---------------------------------------------------------------------------
def is_network_error(error: Exception) -> bool:
    """
    Guess whether an error is a connection/timeout problem.
    The SDK's HTTP library has changed between versions (httpx, httpx2, requests),
    so instead of importing one, we look at the error's class names.
    """
    keywords = ("connect", "timeout", "network", "transport")
    names = [cls.__name__.lower() for cls in type(error).__mro__]
    return any(k in name for name in names for k in keywords)


def ask_gemini(client: genai.Client, prompt: str) -> str | None:
    """
    Send one prompt to Gemini and return the reply text.
    Returns None if something went wrong (the error is printed here).
    """
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        text = response.text
        if not text:
            print("Assistant: Gemini returned an empty response "
                  "(it may have been blocked by a safety filter). Try rephrasing.")
            return None
        return text.strip()

    except errors.ClientError as e:
        # 4xx errors: the problem is on our side (key, quota, model name...)
        message = str(e).lower()
        if e.code in (400, 401, 403) and ("api key" in message or "api_key" in message):
            print("Assistant: Your API key looks invalid. Check GEMINI_API_KEY in .env.")
        elif e.code == 403:
            print("Assistant: Permission denied. Your key may not have access to this model.")
        elif e.code == 404:
            print(f"Assistant: Model '{MODEL}' was not found. Change MODEL in main.py.")
        elif e.code == 429:
            print("Assistant: Rate limit or quota reached. Wait a moment and try again.")
        else:
            print(f"Assistant: Request rejected ({e.code}): {e.message}")

    except errors.ServerError as e:
        # 5xx errors: the problem is on Google's side
        print(f"Assistant: Gemini server problem ({e.code}). Please try again shortly.")

    except Exception as e:  # last safety net so the program never crashes
        if is_network_error(e):
            print("Assistant: Could not reach Gemini. Check your internet connection.")
        else:
            print(f"Assistant: Unexpected error: {e}")

    return None


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main() -> None:
    client = create_client()

    print(LINE)
    print("          MY GEMINI AI ASSISTANT")
    print(LINE)
    print()
    print("Assistant: Hello! How can I help you?")
    print("(Type 'exit' or 'quit' to leave.)")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):  # Ctrl+C or Ctrl+D / Ctrl+Z
            print("\n\nAssistant: Goodbye!")
            break

        if not user_input:
            print("Assistant: Please type a question first.")
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("\nAssistant: Goodbye!")
            break

        reply = ask_gemini(client, user_input)
        if reply:
            print(f"\nAI: {reply}")


if __name__ == "__main__":
    main()