"""
File-based transport adapter for Hannibal RPC.

Sends commands to the game by writing JSON files and receives responses by reading files.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional


class FileTransport:
    """
    File-based transport for sending commands to Hannibal and receiving responses.

    Uses:
    - Command file: ~/.config/0ad/config/hannibal_rpc_command.json
    - Response file: ~/.config/0ad/config/hannibal_rpc_response.json
    """

    def __init__(
        self,
        command_path: Optional[Path] = None,
        response_path: Optional[Path] = None,
        default_timeout: float = 5.0,
    ):
        """
        Initialize the transport.

        Args:
            command_path: Path to write commands to
            response_path: Path to read responses from
            default_timeout: Default timeout for recv operations in seconds
        """
        config_dir = Path.home() / ".config" / "0ad" / "config"

        self.command_path = command_path or (config_dir / "hannibal_rpc_command.json")
        self.response_path = response_path or (config_dir / "hannibal_rpc_response.json")
        self.default_timeout = default_timeout

        # Ensure config directory exists
        self.command_path.parent.mkdir(parents=True, exist_ok=True)

    def send(self, request: Dict[str, Any]) -> str:
        """
        Send a request to the game.

        Args:
            request: Request dictionary (must include 'action' key)

        Returns:
            correlation_id for this request
        """
        # Generate correlation_id if not provided
        if "correlation_id" not in request:
            request["correlation_id"] = str(uuid.uuid4())

        correlation_id = request["correlation_id"]

        # Write command file
        command_json = json.dumps(request, indent=2, sort_keys=True)
        self.command_path.write_text(command_json + "\n", encoding="utf-8")

        return correlation_id

    def recv(self, correlation_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Receive a response for a specific correlation_id.

        Args:
            correlation_id: The correlation ID to wait for
            timeout: Timeout in seconds (uses default_timeout if None)

        Returns:
            Response dictionary

        Raises:
            TimeoutError: If response not received within timeout
        """
        timeout = timeout if timeout is not None else self.default_timeout
        start_time = time.time()
        poll_interval = 0.1  # Check every 100ms

        while time.time() - start_time < timeout:
            if not self.response_path.exists():
                time.sleep(poll_interval)
                continue

            try:
                response_json = self.response_path.read_text(encoding="utf-8")
                response = json.loads(response_json)

                # Check if this response is for our correlation_id
                if response.get("correlation_id") == correlation_id:
                    # Clear the response file so we don't read it again
                    self.response_path.unlink()
                    return response

            except (json.JSONDecodeError, OSError):
                # File might be being written, try again
                pass

            time.sleep(poll_interval)

        raise TimeoutError(
            f"No response received for correlation_id={correlation_id} within {timeout}s"
        )

    def send_and_recv(
        self,
        request: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Send a request and wait for the response.

        Args:
            request: Request dictionary
            timeout: Timeout in seconds

        Returns:
            Response dictionary
        """
        correlation_id = self.send(request)
        return self.recv(correlation_id, timeout)

    def clear_stale_files(self):
        """
        Clear any stale command/response files.

        Useful before starting a new session.
        """
        if self.command_path.exists():
            self.command_path.unlink()
        if self.response_path.exists():
            self.response_path.unlink()
