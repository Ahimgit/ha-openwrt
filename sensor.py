import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensors.cpu import CpuSensor
from .sensors.thermal import ThermalSensorFactory
from .ubus.client import UbusClient
from .ubus.sysinfo_api import SysinfoAPI
from .ubus.thermal_api import ThermalAPI

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.debug("lifecycle: sensor async_setup_entry")

    config = entry.data
    config_instance_id = entry.entry_id

    ubus = UbusClient(config["url"], config["username"], config["password"])

    tapi = ThermalAPI(ubus)
    sapi = SysinfoAPI(ubus)
    tsf = ThermalSensorFactory(tapi)

    sensors_thermal = await tsf.create_sensors(hass, config_instance_id, config["thermal_path"])
    sensor_cpu = CpuSensor(hass, sapi, config_instance_id)
    sensors = sensors_thermal + [sensor_cpu]
    async_add_entities(sensors, update_before_add=True)


async def async_unload_entry(hass: HomeAssistant,
                             entry: ConfigEntry) -> bool:
    LOGGER.debug("lifecycle: sensor async_unload_entry")
    return True  # todo unload client
