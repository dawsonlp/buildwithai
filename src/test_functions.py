#!/usr/bin/env python

# import inspect

from dotenv import load_dotenv

from buildwithai.langchain_tools import (
    get_summarized_jira_issue,
    get_ticket_description,
)


def test_description() -> None:
    load_dotenv()

    description = get_ticket_description.invoke("Forge-10")
    assert (
        description
        == "After some discussion with chatgpt, chose the LangChain library for this. Essentially the POC is to read a Jira ticket, extract the requirements, write some code to implement the requirements, add it to a project and check it in to jira."
    )  # nosec
    print(description)


def test_summarized_issue() -> None:
    load_dotenv()

    issue = get_summarized_jira_issue.invoke("Forge-10")
    print(issue)


if __name__ == "__main__":
    test_description()
    test_summarized_issue()
