import sys
import json
import time
from dotenv import load_dotenv
from agno.exceptions import ModelProviderError

load_dotenv()

from agno.agent import Agent
from agno.tools.e2b import E2BTools
from agno.models.google import Gemini

def main():
    """
    This script uses a multi-agent system with dynamic agent creation.
    1. Chat Agent: The primary interface with the user. Decides whether to answer directly or delegate.
    2. Coder Agent: If a task is delegated, this agent writes the Python code for a new, specialized agent.
    3. Code Executor Agent: Executes the newly generated agent's code in a sandbox.
    """
    # 1. Get user request from command line arguments
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = input("Enter your request for Python code generation: ")

    print(f"User request: {user_request}")

    # 2. Define the agents
    chat_agent = Agent(
        model=Gemini(id="gemini-2.5-flash"),
        system_message=(
            "You are a helpful assistant. First, try to answer the user's request directly. "
            "If the request requires writing code, accessing the file system, or performing complex, multi-step tasks, "
            "you must respond with a single JSON object: "
            "{\"delegate_to_coder\": true, \"task_for_coder\": \"<detailed description of the task for the coder agent>\"}. "
            "Otherwise, provide your answer in plain text."
        )
    )

    coder_agent = Agent(
        model=Gemini(id="gemini-2.5-flash"),
        system_message=(
            "You are an expert Python programmer specializing in agentic design. Your task is to write the Python code for a "
            "complete, self-contained agent that can solve the given task. The agent you create will be executed in a sandboxed environment. "
            "The agent should be written in a single Python script. The script should take the original user request as input "
            "and print the final result to the console. Make sure the agent code is complete and can be executed directly."
            "Please write down the python code into a single file in the ./agents/ directory with the filename format: agent_<functionality>.py"
        )
    )

    e2b_tools = E2BTools()
    code_executor_agent = Agent(
        model=Gemini(id="gemini-2.5-flash"),
        tools=[e2b_tools.run_python_code],
        system_message="You are a code executor. Your task is to run the provided Python script in a sandboxed environment."
    )

    # 3. Start the workflow with the Chat Agent
    print("\n--- Contacting Chat Agent ---\n")
    try:
        chat_output = chat_agent.run(user_request)
        
        # Try to parse the output as JSON to check for delegation
        try:
            delegation_data = json.loads(chat_output.content)
            if delegation_data.get("delegate_to_coder"):
                task_for_coder = delegation_data.get("task_for_coder")
                print("Chat Agent is delegating the task to the Coder Agent.")
                
                # 4. Coder Agent generates the new agent code
                print("\n--- Contacting Coder Agent ---\n")
                generated_agent_code = coder_agent.run(task_for_coder).content
                print("\n--- Generated Agent Code ---\n")
                print(generated_agent_code)
                print("\n--- End of Generated Agent Code ---\n")
                
                # 5. Code Executor Agent runs the new agent
                print("\n--- Contacting Code Executor Agent ---\n")
                execution_prompt = f"Run the following Python script: \n\n{generated_agent_code}"
                execution_result = code_executor_agent.run(execution_prompt).content
                print("\n--- Execution Output ---\n")
                print(execution_result)
                print("\n--- End of Execution Output ---\n")
                
            else:
                # No delegation, print the chat agent's direct answer
                print("\n--- Chat Agent Response ---\n")
                print(chat_output.content)
                print("\n--- End of Response ---\n")

        except (json.JSONDecodeError, AttributeError):
            # Not a JSON response, so it's a direct answer
            print("\n--- Chat Agent Response ---\n")
            print(chat_output.content)
            print("\n--- End of Response ---\n")

    except ModelProviderError as e:
        if e.__cause__ and "RESOURCE_EXHAUSTED" in str(e.__cause__):
            print("\n--- Error ---")
            print("You have exceeded your Gemini API quota. Please check your plan and billing details at https://ai.google.dev/gemini-api/docs/rate-limits")
        else:
            print(f"An API error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    print("\n--- Task Complete ---\n")

if __name__ == "__main__":
    main()