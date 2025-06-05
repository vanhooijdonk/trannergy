"""Update coordinator for the Trannergy integration."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .trannergy import ReadTrannergyData, TrannergyConnectionError

_LOGGER = logging.getLogger(__name__)


class TrannergyUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """The Trannergy update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        ip_address: str,
        port: int,
        device_serial_number: int,
        inverter_serial_number: int,
        enable_3_phase: bool,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.ip_address = ip_address
        self.port = port
        self.device_serial_number = device_serial_number
        self.inverter_serial_number = inverter_serial_number
        self.enable_3_phase = enable_3_phase

        self.trannergy = ReadTrannergyData(
            inverter_ip=self.ip_address,
            inverter_port=self.port,
            device_serial_number=self.device_serial_number,
            inverter_serial=self.inverter_serial_number,
            enable_3_phase=self.enable_3_phase,
        )

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch updated data from the Trannergy inverter."""
        try:
            data = await self.hass.async_add_executor_job(self.trannergy.getdata)
        except TrannergyConnectionError as err:
            raise UpdateFailed(err) from err
        except Exception as err:
            raise UpdateFailed(err) from err

        if not data:
            raise UpdateFailed("No data was returned from the Trannergy inverter")

        return data
