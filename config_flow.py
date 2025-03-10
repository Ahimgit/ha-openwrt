import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback

from .const import DOMAIN
from .const import NAME

LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        LOGGER.debug("lifecycle: configflow async_step_user")

        if user_input is not None:
            return self.async_create_entry(title=NAME, data=user_input)
        return self.async_show_form(step_id="user", data_schema=get_data_schema())

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry):
        LOGGER.debug("lifecycle: configflow async_get_options_flow")
        return OptionsFlow()


class OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        LOGGER.debug("lifecycle: optionsflow async_step_init")
        entry = self.hass.config_entries.async_get_entry(self.handler)
        if user_input is not None:
            self.hass.config_entries.async_update_entry(entry, data=user_input)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(step_id="init", data_schema=get_data_schema(entry.data))


def get_data_schema(data=None):
    if data is None:
        data = {}
    return vol.Schema({
        vol.Required("url", default=data.get("url", "http://192.168.1.1/ubus")): str,
        vol.Required("username", default=data.get("username", "ha")): str,
        vol.Required("password", default=data.get("password", "")): str,
        vol.Optional("thermal_path", default=data.get("thermal_path", "/sys/class/thermal")): str,
    })
