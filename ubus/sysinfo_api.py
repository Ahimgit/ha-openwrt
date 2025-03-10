import logging
from dataclasses import dataclass

from ..ubus.client import UBUS_STATUS_OK
from ..ubus.client import UbusClient
from ..ubus.client import UbusClientError

LOGGER = logging.getLogger(__name__)


@dataclass
class SystemInfo:
    localtime: int | None = None
    uptime: int | None = None
    load_1m: float | None = None
    load_5m: float | None = None
    load_15m: float | None = None
    memory_total: int | None = None
    memory_free: int | None = None
    memory_shared: int | None = None
    memory_buffered: int | None = None
    memory_available: int | None = None
    memory_cached: int | None = None
    root_total: int | None = None
    root_free: int | None = None
    root_used: int | None = None
    root_avail: int | None = None
    tmp_total: int | None = None
    tmp_free: int | None = None
    tmp_used: int | None = None
    tmp_avail: int | None = None
    swap_total: int | None = None
    swap_free: int | None = None


class SysinfoAPI:
    def __init__(self, ubus: UbusClient) -> None:
        self.ubus = ubus

    async def get_system_info(self) -> SystemInfo:
        # {"jsonrpc":"2.0","id":1,"result":[0,
        # {"localtime":1741131431,"uptime":385729,"load":[1440,3392,384],
        # "memory":{"total":244559872,"free":120569856,"shared":4370432,"buffered":0,"available":115216384,"cached":35377152},
        # "root":{"total":62732,"free":59060,"used":3672,"avail":55812},
        # "tmp":{"total":119412,"free":115144,"used":4268,"avail":115144},
        # "swap":{"total":0,"free":0}}]}
        status, rs = await self.ubus.call("system", "info", {})
        if status != UBUS_STATUS_OK:
            raise UbusClientError(f"Fetching system info failed. Service returned non-zero status {status}")
        else:
            return SystemInfo(
                load_1m=rs["load"][0]
            )
