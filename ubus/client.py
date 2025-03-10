import logging

import aiohttp

LOGGER = logging.getLogger(__name__)

UBUS_RPC_STATUS_PERMISSION_DENIED = -32002

UBUS_STATUS_OK = 0
UBUS_STATUS_INVALID_COMMAND = 1
UBUS_STATUS_INVALID_ARGUMENT = 2
UBUS_STATUS_METHOD_NOT_FOUND = 3
UBUS_STATUS_NOT_FOUND = 4
UBUS_STATUS_NO_DATA = 5
UBUS_STATUS_PERMISSION_DENIED = 6
UBUS_STATUS_TIMEOUT = 7
UBUS_STATUS_NOT_SUPPORTED = 8
UBUS_STATUS_UNKNOWN_ERROR = 9
UBUS_STATUS_CONNECTION_FAILED = 10
UBUS_STATUS_NO_MEMORY = 11
UBUS_STATUS_PARSE_ERROR = 12
UBUS_STATUS_SYSTEM_ERROR = 13


class UbusClient:
    UNAUTH_SESSION_ID = "00000000000000000000000000000000"

    def __init__(self, url: str, username: str, password: str, timeout: int = 5):
        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session = aiohttp.ClientSession()
        self.session_token = None

    async def login(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [UbusClient.UNAUTH_SESSION_ID, "session", "login", {
                "username": self.username,
                "password": self.password
            }]
        }
        try:
            async with self.session.post(self.url, json=payload, timeout=self.timeout) as response:
                code, rs = self._get_result(await response.json())
                if code == UBUS_STATUS_OK:
                    self.session_token = rs["ubus_rpc_session"]
                    LOGGER.info("Successfully authenticated with OpenWRT.")
                else:
                    raise UbusClientError(f"Error logging in to ubus: {code}")
        except aiohttp.ClientError as e:
            raise UbusClientError("Error sending request to ubus") from e

    async def call(self, service: str, method: str, params=None) -> tuple[int, dict]:
        if params is None:
            params = {}
        if not self.session_token:
            await self.login()
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [self.session_token, service, method, params]
        }
        try:
            async with self.session.post(self.url, json=payload, timeout=self.timeout) as response:
                code, rs = self._get_result(await response.json())
                if code == UBUS_RPC_STATUS_PERMISSION_DENIED:  # re-auth session
                    await self.login()
                    code, rs = self._get_result(await response.json())
                return code, rs
        except aiohttp.ClientError as e:
            raise UbusClientError("Error sending request to ubus") from e

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    @staticmethod
    def _get_result(data: dict) -> tuple[int, dict]:
        if "error" in data:
            return data["error"]["code"], data
        if "result" in data and data["result"][0] == UBUS_STATUS_OK:
            return UBUS_STATUS_OK, data["result"][1]
        else:
            if "result" not in data:
                return -1, {}
            else:
                return data["result"][0], {}


class UbusClientError(Exception):
    pass
