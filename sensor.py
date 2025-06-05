"""Support for the Trannergy sensor service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TrannergyConfigEntry, TrannergyUpdateCoordinator
from .const import DOMAIN, MANUFACTURER, NAME

ATTRIBUTION = "Data provided by Trannergy inverter"

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class TrannergyEntityDescription(SensorEntityDescription):
    """Describes Trannergy inverter sensor entity."""

    value_fn: Callable[[Any], StateType]


SENSOR_TYPES: tuple[TrannergyEntityDescription, ...] = (
    TrannergyEntityDescription(
        key="yield_total",
        translation_key="yield_today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda data: data.get("yield_total"),
    ),
    TrannergyEntityDescription(
        key="yield_today",
        translation_key="yield_today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda data: data.get("yield_today"),
    ),
    TrannergyEntityDescription(
        key="power_ac1",
        translation_key="power_ac1",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda data: data.get("power_ac1"),
    ),
    TrannergyEntityDescription(
        key="frequency_ac",
        translation_key="frequency_ac",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
        value_fn=lambda data: data.get("frequency_ac"),
    ),
    TrannergyEntityDescription(
        key="voltage_ac1",
        translation_key="voltage_ac1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        value_fn=lambda data: data.get("voltage_ac1"),
    ),
    TrannergyEntityDescription(
        key="ampere_ac1",
        translation_key="ampere_ac1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        value_fn=lambda data: data.get("ampere_ac1"),
    ),
    TrannergyEntityDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: data.get("temperature"),
    ),
    TrannergyEntityDescription(
        key="hrs_total",
        translation_key="hrs_total",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda data: data.get("hrs_total"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TrannergyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Trannergy inverter sensor entities based on a config entry."""
    coordinator = config_entry.runtime_data

    entities = [
        TrannergySensor(coordinator, description) for description in SENSOR_TYPES
    ]

    async_add_entities(entities, False)


class TrannergySensor(CoordinatorEntity[TrannergyUpdateCoordinator], SensorEntity):
    """Define an Trannergy sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    entity_description: TrannergyEntityDescription

    def __init__(
        self,
        coordinator: TrannergyUpdateCoordinator,
        description: TrannergyEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        _device_id = f"{coordinator.inverter_serial_number}"

        self.entity_description = description
        self._attr_unique_id = f"{_device_id}-{description.key.lower()}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, _device_id)},
            manufacturer=MANUFACTURER,
            name=NAME,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator.data)
