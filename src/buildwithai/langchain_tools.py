import os
from typing import Any

from git import Repo
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool

from connections.connector import JiraConnector


class JiraService:
    def __init__(self, jira_url: str, jira_user: str, jira_token: str):
        """Initializes the service with a JiraConnector instance."""
        self.connector = JiraConnector(jira_url, jira_user, jira_token)

    def get_simplified_issue(self, issue_key: str) -> Any:
        """Fetches a simplified view of a Jira issue.

        Args:
        - issue_key (str): The Jira issue key.
        Returns:
        - dict: The simplified issue details.
        """
        connection = self.connector.get_connection()

        def request() -> Any:
            issue = connection.issue(issue_key)
            return {
                "summary": issue.fields.summary,
                "description": issue.fields.description,
                "status": issue.fields.status.name,
                "comments": (
                    [
                        {
                            "author": comment.author.displayName,
                            "body": comment.body,
                            "created": comment.created,
                        }
                        for comment in issue.fields.comment.comments
                    ]
                    if issue.fields.comment
                    else []
                ),
            }

        return self.connector.handle_request_with_retries(request)

    def get_ticket_description(self, ticket_id: str) -> Any:
        """Fetches the description of a Jira ticket."""
        connection = self.connector.get_connection()

        def request() -> str:
            issue = connection.issue(ticket_id)
            return str(issue.fields.description)

        return self.connector.handle_request_with_retries(request)

    def add_comment(self, ticket_id: str, comment: str) -> Any:
        """Adds a comment to a Jira ticket."""

        connection = self.connector.get_connection()

        def request() -> str:
            res = connection.add_comment(ticket_id, comment)
            return f"Comment added to ticket {ticket_id}. Comment ID: {res.id}"

        return self.connector.handle_request_with_retries(request)


# OK, this is funky, and I will try to work out how the @tool decorator works so that it is unnecessary for the jira
# tools I'm defining here.

global jira_service
jira_service: JiraService


def set_jira_service(jira_service_instance: JiraService) -> None:
    """Sets the Jira service instance to be used by the tools.

    This needs to be called before using the Jira tools. Really I want
    the tools to be in a class, but not sure how to do that in langchain
    yet.
    """
    global jira_service
    jira_service = jira_service_instance


@tool
def get_summarized_jira_issue(issue_key: str) -> Any:
    """Fetches a comprehensive view of a Jira issue.

    This includes significant detail including all of the comments.
    Choose this if you need a more detailed view of the issue.
    """
    return jira_service.get_simplified_issue(issue_key)  # noqa: F821


@tool
def comment_on_ticket(ticket_id: str, comment: str) -> Any:
    """Adds a comment to a Jira ticket."""
    return jira_service.add_comment(ticket_id, comment)  # noqa: F821


@tool
def get_ticket_description(ticket_id: str) -> Any:
    """Fetches just the description field of a Jira ticket."""
    return jira_service.get_ticket_description(ticket_id)  # noqa: F821


# Define tools for project management
@tool
def create_project(project_name: str) -> Any:
    """Creates a new jira project directory."""
    os.makedirs(project_name, exist_ok=True)
    return f"Project {project_name} created."


@tool
def generate_code(description: str) -> Any:
    """Generates Python code based on a description."""
    client = init_chat_model(
        "gpt-4o-mini",
        model_provider="openai",
        temperature=0,
        api_key=os.getenv('CHATGPT_API_KEY'),
    )
    program_system = """You are an expert python developer.
    Implement a python program based on the user's description.
    It should use best practices for the python community.
    Also, use descriptive names rather than excessive comments.
    If it helps legibility, break out sub-functions with descriptive names.
    Comments should indicate intent and design, not repeat the code.
    Make the code as simple as possible, but no simpler.
    The code should be encapsulated in a function, for a script, the major functionality should still be wrapped in 
    a function.
    If you are asked for a script, use the fire library to make it easy to use, but don't over-engineer it.
    """

    prompt = ChatPromptTemplate.from_messages(
        [("system", program_system), ("human", "{input}")]
    )
    chain = prompt | client
    return chain.invoke(description)


@tool
def commit_code_to_github(project_name: str, code: str) -> Any:
    """Commits the generated code to a GitHub repository."""
    repo = Repo.init(project_name)
    with open(f'{project_name}/src/implementation.py', 'w') as f:
        f.write(code)

    repo.index.add([f'{project_name}/src/implementation.py'])
    repo.index.commit('Initial implementation')

    github_access_token = os.getenv('GITHUB_ACCESS_TOKEN')
    origin = repo.create_remote(
        'origin',
        f'https://{github_access_token}@github.com/yourusername/{project_name}.git',
    )
    origin.push(refspec='main:main')
    return f"Code committed to GitHub repository: {project_name}"
