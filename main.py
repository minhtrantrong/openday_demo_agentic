
import sys
import time
from dotenv import load_dotenv
from agno.exceptions import ModelProviderError

load_dotenv()

from agno.agent import Agent
from agno.tools.e2b import E2BTools
from agno.models.google import Gemini

# 1. Get user request from command line arguments
if len(sys.argv) > 1:
    user_request = " ".join(sys.argv[1:])
else:
    user_request = input("Enter your request for Python code generation: ")

print(f"User request: {user_request}")

# 2. Create a "coder" agent to generate the Python code
coder_agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    system_message="You are a Python code generation expert. Your task is to generate Python code based on the user's request. Only output the code, no explanations or markdown."
)

# 3. Generate the Python code
try:
    code_generation_output = coder_agent.run(user_request)
    code_to_run = code_generation_output.content
except ModelProviderError as e:
    if e.__cause__ and "RESOURCE_EXHAUSTED" in str(e.__cause__):
        print("\n--- Error ---")
        print("You have exceeded your Gemini API quota. Please check your plan and billing details at https://ai.google.dev/gemini-api/docs/rate-limits")
        print("--- End of Error ---")
        sys.exit(1)
    else:
        raise e


print("\n--- Generated Code ---\n")
print(code_to_run)
print("\n--- End of Generated Code ---\n")

# Add a delay to avoid rate limiting
time.sleep(1)

# 4. The existing "executor" agent will then take this generated code and run it in the sandbox.
# Instantiate the E2BTools toolkit
# Make sure to have the E2B_API_KEY environment variable set
e2b_tools = E2BTools()

# Create an Agent instance with the E2BTools toolkit
executor_agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    tools=[e2b_tools.run_python_code],
)

# Run the Python code in the sandbox using the agent
try:
    run_output = executor_agent.run(f"Run the following python code in the sandbox: {code_to_run}")
except ModelProviderError as e:
    if e.__cause__ and "RESOURCE_EXHAUSTED" in str(e.__cause__):
        print("\n--- Error ---")
        print("You have exceeded your Gemini API quota. Please check your plan and billing details at https://ai.google.dev/gemini-api/docs/rate-limits")
        print("--- End of Error ---")
        sys.exit(1)
    else:
        raise e

# Print the output
print("\n--- Execution Output ---\n")
print(run_output.content)
