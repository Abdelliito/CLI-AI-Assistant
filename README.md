# Gemini AI Assistant

A small command-line chatbot that sends prompts to Google's Gemini API and
prints the responses in an interactive terminal session.

## Requirements

- Python 3.10 or newer
- A Google Gemini API key

## Setup

1. Create and activate a virtual environment (recommended):

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your API key:

   ```text
   GEMINI_API_KEY=your_real_api_key
   ```

Do not commit `.env` or share your API key.

## Run

```powershell
python main.py
```

Type a question at the `You:` prompt. Enter `exit` or `quit` to end the
session. `Ctrl+C` and end-of-file input (`Ctrl+Z`, then Enter in Windows) also
exit cleanly.

## How it works

- Loads `GEMINI_API_KEY` from `.env`.
- Uses the Google Gen AI SDK to call the configured Gemini Flash model.
- Displays helpful messages for invalid credentials, quota limits, unavailable
  models, network failures, and other API errors.
- Keeps running after an individual request fails so another prompt can be
  entered.

The model name is configured near the top of `main.py` in the `MODEL`
constant. Change it there if the configured model is unavailable for your API
key.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | CLI application and Gemini API integration |
| `requirements.txt` | Python dependencies |
| `.env` | Local API key configuration (create this file; do not commit it) |
