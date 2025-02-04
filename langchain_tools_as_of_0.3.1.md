
# tools and utilities for working with language chains

## How tools are created

The preferred approach is to use the `@tools` decorator from the `langchain` package. This decorator is used to define a function as a tool.
    
    ```python
    from langchain.tools import tool
    @tool
    def simple_test_tool(who: str, times: str) -> str:
        """Just a simple test tool, takes a string representing a name and returns a greeting"""
        t = int(times)
        return f"{who}, hello from the simple test tool, {t} times"
    
    simple_test_tool.invoke(input={'who':"world", 'times':"3"})
    ```

However the @tool decorator doesn't support member functions of a class, and may have other limitations. 
There is a Structured_Tool class that may help. It is defined in the `langchain.tools` module.

    ```python
    from langchain.tools import Structured_Tool
    
    class SomeTool(Structured_Tool):
        def __init__(self, input_text: str):
            self.input_text = input_text

        def run(self) -> str:
            pass
    ```