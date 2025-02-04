from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Dict, Tuple

from jira import JIRA, JIRAError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed


class BaseServiceClient(ABC):
    def __init__(self, max_retries: int = 3, delay: int = 2):
        """Initializes the base service client with retry logic using Tenacity.

        Args:
        - max_retries (int): Maximum number of retry attempts.
        - delay (int): Delay in seconds between retry attempts.
        """
        self.max_retries = max_retries
        self.delay = delay
        self.connection = None

    @abstractmethod
    def connect(self) -> None:
        """Method to establish a connection to the service.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def is_token_expired(self, error: Any) -> bool:
        """Checks if a token or session has expired.

        Must be implemented by subclasses.
        """
        pass

    @retry(
        stop=stop_after_attempt(3),  # Stop retrying after 3 attempts
        wait=wait_fixed(2),  # Wait 2 seconds between retries
        retry=retry_if_exception_type(
            ConnectionError
        ),  # Retry only on connection errors
    )
    def reconnect(self) -> None:
        """Reconnect to the service, retrying a set number of times using
        Tenacity."""
        self.connect()  # This will automatically retry if it raises a ConnectionError

    def ensure_connection(self) -> None:
        """Ensures the connection is established, reconnecting if necessary."""
        if not self.connection:
            self.reconnect()

    def handle_request_with_retries(
        self, request_func: Callable, *args: Tuple[Any], **kwargs: Dict[str, Any]
    ) -> Any:
        """Executes a request with automatic retry on failure due to expired
        token or connection.

        Args:
        - request_func: The function to execute the request.
        - *args, **kwargs: Arguments to pass to the request function.
        Returns:
        - The result of the request.
        """
        try:
            self.ensure_connection()
            return request_func(*args, **kwargs)
        except Exception as e:
            if self.is_token_expired(e):
                self.reconnect()  # Reconnect if token expired
                return request_func(*args, **kwargs)  # Retry after reconnection
            else:
                raise e


class JiraConnector(BaseServiceClient):
    def __init__(
        self,
        jira_url: str,
        jira_user: str,
        jira_token: str,
        max_retries: int = 3,
        delay: int = 2,
    ):
        super().__init__(max_retries, delay)
        self.server = jira_url
        self.username = jira_user
        self.api_token = jira_token
        self.connection = None

    def connect(self) -> None:
        """Establishes a connection to Jira."""
        if not self.server or not self.username or not self.api_token:
            raise ValueError("Missing Jira credentials.")
        try:
            self.connection = JIRA(
                server=self.server, basic_auth=(self.username, self.api_token)
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Jira: {str(e)}")

    def is_token_expired(self, error: Any) -> bool:
        """Checks if the token has expired (based on a 401 error from Jira)."""
        return isinstance(error, JIRAError) and error.status_code == 401

    def get_connection(self) -> JIRA:
        """Ensures a connection is established and returns the Jira connection
        object."""
        self.ensure_connection()
        return self.connection
