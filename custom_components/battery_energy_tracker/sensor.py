"""Battery Energy Tracker sensor platform."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the battery tracker sensors from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        TotalDischargeEnergySensor(coordinator),
        TotalChargeEnergySensor(coordinator),
        EnergySinceLastChargeSensor(coordinator),
        EstimatedChargeTimeSensor(coordinator),
        ChargeStatusSensor(coordinator),
        DiagnosticSensor(coordinator)
    ]
    
    async_add_entities(entities)

class BatteryEnergySensor(CoordinatorEntity, SensorEntity):
    """Base class for battery energy sensors."""
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "battery_energy_tracker")},
            "name": "Battery Energy Tracker",
            "manufacturer": "Custom",
            "model": "Battery Energy Monitor",
        }


class TotalDischargeEnergySensor(BatteryEnergySensor):
    """Sensor to track total discharged energy."""
    
    _attr_name = "Total Discharge Energy"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:battery-minus-outline"
    
    @property
    def unique_id(self):
        """Return unique ID for the sensor."""
        return f"{DOMAIN}_total_discharge_energy"
        
    @property
    def native_value(self):
        """Return the total discharge energy."""
        if self.coordinator.data and "total_discharge_kwh" in self.coordinator.data:
            return round(self.coordinator.data["total_discharge_kwh"], 2)
        return 0