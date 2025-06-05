"""Config flow for Trannergy integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
)
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_DEVICE_SERIAL_NUMBER,
    CONF_ENABLE_3_PHASE,
    CONF_INVERTER_SERIAL_NUMBER,
    DOMAIN,
    NAME,
)
from .trannergy import ReadTrannergyData

_LOGGER = logging.getLogger(__name__)


class ReadTrannergyDataError(HomeAssistantError):
    """Error reading trannergy data."""


class TrannergyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Trannergy."""

    async def async_step_user(self, user_input) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                trannergy = ReadTrannergyData(
                    inverter_ip=user_input.get(CONF_IP_ADDRESS),
                    inverter_port=user_input.get(CONF_PORT),
                    device_serial_number=user_input.get(CONF_DEVICE_SERIAL_NUMBER),
                    inverter_serial=user_input.get(CONF_INVERTER_SERIAL_NUMBER),
                    enable_3_phase=user_input.get(CONF_ENABLE_3_PHASE, False),
                )
                data = trannergy.getdata()
                _LOGGER.info(data)
            except Exception as e:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "Error: " + str(e)
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, NAME),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=NAME): cv.string,
                    vol.Required(CONF_IP_ADDRESS, default=""): cv.string,
                    vol.Optional(CONF_PORT, default=8899): cv.positive_int,
                    vol.Required(CONF_DEVICE_SERIAL_NUMBER, default=""): cv.string,
                    vol.Required(CONF_INVERTER_SERIAL_NUMBER, default=""): cv.string,
                    vol.Optional(CONF_SCAN_INTERVAL, default=60): cv.positive_int,
                    vol.Optional(CONF_ENABLE_3_PHASE): cv.boolean,
                }
            ),
            errors=errors,
        )
