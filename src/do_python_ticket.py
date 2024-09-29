import os

import fire
from langchain import LLMChain
from langchain.chat_models import init_chat_model

from buildwithai.langchain_tools import (
    comment_on_ticket,
    get_summarized_jira_issue,
    get_ticket_description,
)


# Create a chain that uses the tools
llm = init_chat_model(
    provider="openai", model="gpt-4o-mini", api_key=os.getenv('CHATGPT_API_KEY')
)

# Old: llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv('CHATGPT_API_KEY'))

chain = LLMChain(
    llm=llm,
    tools=[get_summarized_jira_issue, comment_on_ticket, get_ticket_description],
)


# Main function to handle command-line operations
def handle_jira_ticket(ticket_id: str, project_name: str) -> None:
    """Handles a Jira ticket by creating a project, generating code, and
    committing to GitHub."""

    description = chain.run(f"get_ticket_description for {ticket_id}")
    print(f"Ticket Description: {description}")

    chain.run(f"create_project {project_name}")
    print(f"Created Project: {project_name}")

    code = chain.run(f"generate_code based on this: {description}")
    print(f"Generated Code: {code}")

    chain.run(f"commit_code_to_github for {project_name} with this code: {code}")
    print(f"Committed Code to GitHub for Project: {project_name}")

    repo_url = f"https://github.com/yourusername/{project_name}"
    chain.run(
        f"comment_on_ticket {ticket_id} with this comment: Implementation complete. Repository: {repo_url}"
    )
    print(f"Commented on Ticket {ticket_id} with Repository URL: {repo_url}")


# Use fire to expose the function to the command line
if __name__ == '__main__':
    fire.Fire(handle_jira_ticket)
