"""Init for Trannergy integration."""

import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICE_SERIAL_NUMBER,
    CONF_INVERTER_SERIAL_NUMBER,
)
from .coordinator import TrannergyUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]
type TrannergyConfigEntry = ConfigEntry[TrannergyUpdateCoordinator]

DOMAIN = "trannergy"


async def async_setup_entry(hass: HomeAssistant, entry: TrannergyConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    ip_address = entry.data.get(CONF_IP_ADDRESS)
    port = entry.data.get(CONF_PORT)
    device_serial_number = entry.data.get(CONF_DEVICE_SERIAL_NUMBER)
    inverter_serial_number = entry.data.get(CONF_INVERTER_SERIAL_NUMBER)
    update_interval = datetime.timedelta(seconds=entry.data.get(CONF_SCAN_INTERVAL))

    coordinator = TrannergyUpdateCoordinator(
        hass,
        ip_address,
        port,
        device_serial_number,
        inverter_serial_number,
        update_interval,
    )

    # Sync with Coordinator
    await coordinator.async_config_entry_first_refresh()

    # Store Entity and Initialize Platforms
    entry.runtime_data = coordinator

    # Listen for option changes
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
