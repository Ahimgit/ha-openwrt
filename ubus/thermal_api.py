import logging

from ..ubus.client import UBUS_STATUS_OK
from ..ubus.client import UbusClient
from ..ubus.client import UbusClientError

LOGGER = logging.getLogger(__name__)


class ThermalAPI:
    def __init__(self, ubus: UbusClient):
        self.ubus = ubus

    async def get_thermal_entries(self, thermal_base_path: str) -> list[tuple[str, str]]:
        LOGGER.debug(f"Fetching thermal_entries for base path {thermal_base_path}")
        status, rs = await self.ubus.call("file", "list", {"path": thermal_base_path})
        if status != UBUS_STATUS_OK or "entries" not in rs:
            raise UbusClientError(f"Fetching thermal_entries failed. Service returned non-zero status {status}")
        results = []
        for entry in rs["entries"]:
            if entry.get("type") == "directory":
                thermal_name = entry.get("name")
                thermal_path = f"{thermal_base_path}/{thermal_name}/temp"
                thermal_file_exists = await self._check_file_exists(thermal_path)
                if thermal_file_exists:
                    results.append((thermal_name, thermal_path))
        return results

    async def get_thermal_temperature(self, thermal_path: str) -> float:
        # {'jsonrpc': '2.0', 'id': 1, 'result': [0, {'data': '61106\n'}]}
        LOGGER.debug(f"Fetching temperature value for path {thermal_path}")
        status, rs = await self.ubus.call("file", "read", {"path": thermal_path})
        if status != UBUS_STATUS_OK or "data" not in rs:
            raise UbusClientError(f"Service returned non-zero status {status}")
        else:
            return int(rs["data"].strip()) / 1000

    async def _check_file_exists(self, file_path: str):
        status, rs = await self.ubus.call("file", "stat", {"path": file_path})
        return status == UBUS_STATUS_OK and "type" in rs and rs["type"] == "file"
