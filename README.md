# AI Agentic Coder

This application uses an AI agent to generate Python code based on a user's request and then executes the code in a secure sandbox environment.And this just a demo code in OpenDay of mine in Greenwich! 

## Prerequisites

- Python 3.13.x
- An E2B API key
- A Google API key for Gemini

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/minhtrantrong/openday_demo_agentic.git
    cd Agentic_AI
    ```

2.  **Create and activate a virtual environment:**

    On macOS and Linux:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

    On Windows:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

## Installation

Install the required Python libraries using pip:

```bash
pip install -r requirements.txt
```

## Configuration

1.  Create a `.env` file in the root of the project directory.

2.  Add your API keys to the `.env` file:

    ```
    E2B_API_KEY="your_e2b_api_key"
    GOOGLE_API_KEY="your_google_api_key"
    ```

    **Note:** The `main.py` script loads these environment variables. The `E2B_API_KEY` is used by the `E2BTools` for the sandbox environment, and the `GOOGLE_API_KEY` is used by the `Gemini` model.

## Usage

Run the `main.py` script from the command line with your request in quotes.

**Example:**

```bash
python3 main.py "create a file named 'example.txt' with the content 'Hello from the agent!'"
```
or just simple: 
```bash
python3 main.py
```

If you run the script without any arguments, it will prompt to ask you input the request for python code.
