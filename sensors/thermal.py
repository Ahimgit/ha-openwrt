import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass, SensorDeviceClass
from homeassistant.const import UnitOfTemperature, EntityCategory
from homeassistant.core import HomeAssistant

from ..ubus.thermal_api import ThermalAPI

LOGGER = logging.getLogger(__name__)


class ThermalSensorFactory:
    def __init__(self, thermal_api: ThermalAPI):
        self.thermal_api = thermal_api

    async def create_sensors(
            self,
            hass: HomeAssistant,
            config_instance_id: str,
            thermal_base_path: str):
        LOGGER.debug("lifecycle: thermalsensorfactory create_sensors")
        thermal_entries = await self.thermal_api.get_thermal_entries(thermal_base_path)
        sensors = []
        for thermal_name, thermal_path in thermal_entries:
            sensor_name = f"OpenWRT Thermal {thermal_name.replace('_', ' ').title()}"
            sensor = ThermalSensor(hass, self.thermal_api, thermal_path, sensor_name, config_instance_id)
            sensors.append(sensor)
        return sensors


class ThermalSensor(SensorEntity):
    ENTITY_DESCRIPTION = SensorEntityDescription(
        key="thermal",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:thermometer"
    )

    def __init__(
            self,
            hass: HomeAssistant,
            thermal_api: ThermalAPI,
            thermal_path: str,
            name: str,
            config_instance_id: str
    ) -> None:
        self.hass = hass
        self.thremal_api = thermal_api
        self.thermal_path = thermal_path
        self.entity_description = ThermalSensor.ENTITY_DESCRIPTION
        self._attr_name = name
        self._attr_unique_id = f"{self.entity_description.key}_{config_instance_id}"
        self._attr_native_value: float | None = None

    async def async_update(self) -> None:
        LOGGER.debug("lifecycle: thermalsensor async_update")
        try:
            # {'jsonrpc': '2.0', 'id': 1, 'result': [0, {'data': '61106\n'}]}
            self._attr_native_value = await self.thremal_api.get_thermal_temperature(self.thermal_path)
        except Exception:
            LOGGER.error(f"Failed to fetch temperature from {self.thermal_path}", exc_info=True)
            self._attr_native_value = None
