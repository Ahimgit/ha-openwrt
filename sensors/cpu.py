import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant

from ..ubus.sysinfo_api import SysinfoAPI

LOGGER = logging.getLogger(__name__)


class CpuSensor(SensorEntity):
    ENTITY_DESCRIPTION = SensorEntityDescription(
        key="cpu_total_usage",
        name="OpenWRT CPU Total Usage",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:cpu-32-bit"
    )

    def __init__(
            self,
            hass: HomeAssistant,
            sysinfo_api: SysinfoAPI,
            config_instance_id: str
    ) -> None:
        self.hass = hass
        self.sysinfo_api = sysinfo_api
        self.entity_description = CpuSensor.ENTITY_DESCRIPTION
        self._attr_native_value: float | None = None
        self._attr_unique_id = f"{self.entity_description.key}_{config_instance_id}"

    async def async_update(self) -> None:
        LOGGER.debug("lifecycle: cpusensor async_update")
        try:
            sysinfo = await self.sysinfo_api.get_system_info()
            self._attr_native_value = sysinfo.load_1m / 1000
        except Exception:
            LOGGER.error(f"Failed to fetch cpu load from", exc_info=True)
            self._attr_native_value = None
