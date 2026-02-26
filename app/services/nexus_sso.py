"""
Nexus Mods SSO authentication via WebSocket.
Connects to wss://sso.nexusmods.com, opens browser for user authorization,
and receives the API key automatically when approved.
"""

import json
import threading
import uuid
import webbrowser

import websocket

NEXUS_SSO_URL = "wss://sso.nexusmods.com"
NEXUS_SSO_AUTHORIZE = "https://www.nexusmods.com/sso"
APPLICATION_SLUG = "fromsoft-coop-manager"


class NexusSSOClient:
    """WebSocket-based Nexus Mods SSO client.

    Usage:
        client = NexusSSOClient()
        client.start()          # connects WS + opens browser
        # poll periodically:
        key, err = client.poll()
        if key:  ...            # got the API key
        if err:  ...            # something went wrong
        client.stop()           # clean up
    """

    def __init__(self):
        self._api_key: str | None = None
        self._error: str | None = None
        self._connection_token: str | None = None
        self._uuid: str = str(uuid.uuid4())
        self._done = threading.Event()
        self._ws: websocket.WebSocketApp | None = None
        self._thread: threading.Thread | None = None

    # ── public API ────────────────────────────────────────

    def start(self):
        """Connect to the SSO WebSocket and open the browser for authorization."""
        self._api_key = None
        self._error = None
        self._done.clear()

        self._ws = websocket.WebSocketApp(
            NEXUS_SSO_URL,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._thread = threading.Thread(target=self._run_ws, daemon=True)
        self._thread.start()

    def poll(self) -> tuple[str | None, str | None]:
        """Non-blocking check for results. Returns (api_key, error)."""
        return self._api_key, self._error

    def stop(self):
        """Close the WebSocket connection and clean up."""
        self._done.set()
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass

    # ── internal ──────────────────────────────────────────

    def _run_ws(self):
        try:
            self._ws.run_forever()
        except Exception as e:
            self._error = str(e)
            self._done.set()

    def _on_open(self, ws):
        """Send SSO request and open browser."""
        data = {
            "id": self._uuid,
            "token": self._connection_token,
            "protocol": 2,
        }
        ws.send(json.dumps(data))

    def _on_message(self, ws, message):
        """Handle SSO responses: connection_token or api_key."""
        try:
            response = json.loads(message)
        except (json.JSONDecodeError, TypeError):
            return

        if not response.get("success"):
            self._error = response.get("error", "SSO authorization failed")
            self._done.set()
            return

        data = response.get("data", {})

        if "connection_token" in data:
            # First response — store token for reconnection, then open browser
            self._connection_token = data["connection_token"]
            url = f"{NEXUS_SSO_AUTHORIZE}?id={self._uuid}&application={APPLICATION_SLUG}"
            webbrowser.open(url)

        elif "api_key" in data:
            # User authorized — we have the key
            self._api_key = data["api_key"]
            self._done.set()
            ws.close()

    def _on_error(self, ws, error):
        self._error = str(error) if error else "WebSocket connection error"
        self._done.set()

    def _on_close(self, ws, close_status_code, close_msg):
        # If we don't have a key yet and weren't intentionally stopped,
        # this is an unexpected disconnect
        if not self._api_key and not self._done.is_set():
            self._error = "Connection closed before authorization completed"
            self._done.set()
