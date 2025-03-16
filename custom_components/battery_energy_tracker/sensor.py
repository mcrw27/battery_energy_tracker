"""Battery Energy Tracker sensor platform."""
import logging
import asyncio
from datetime import timedelta
from typing import Optional

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_BATTERY_COUNT,
    CONF_CHARGE_RATE,
    CONF_ENTITY_PATTERNS,
    CONF_SCALE_FACTOR,
    CONF_MANUAL_ENTITIES,
    CONF_STARTUP_DELAY,
    DEFAULT_CHARGE_RATE,
    DEFAULT_SCALE_FACTOR,
    ATTR_TOTAL_DISCHARGE,
    ATTR_TOTAL_CHARGE,
    ATTR_ESTIMATED_CHARGE_TIME,
    ATTR_LAST_RESET,
    ATTR_LAST_CHARGE_STARTED,
    ATTR_LAST_CHARGE_COMPLETED,
    ATTR_CHARGE_DURATION,
    ATTR_ENERGY_SINCE_LAST_CHARGE,
)
from .coordinator_base import BatteryEnergyCoordinator

_LOGGER = logging.getLogger(__name__)

# Sensor platform schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_BATTERY_COUNT, default=4): cv.positive_int,
        vol.Optional(CONF_CHARGE_RATE, default=DEFAULT_CHARGE_RATE): cv.positive_float,
        vol.Optional(CONF_ENTITY_PATTERNS): {
            vol.Optional("discharge"): cv.string,
            vol.Optional("charge"): cv.string,
            vol.Optional("current"): cv.string,
        },
        vol.Optional(CONF_SCALE_FACTOR, default=DEFAULT_SCALE_FACTOR): cv.positive_float,
        vol.Optional(CONF_MANUAL_ENTITIES): {
            vol.Required("discharge"): [cv.entity_id],
            vol.Required("charge"): [cv.entity_id],
            vol.Required("current"): [cv.entity_id],
        },
        vol.Optional(CONF_STARTUP_DELAY, default=0): cv.positive_int,
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the battery tracker sensors."""
    
    battery_count = config.get(CONF_BATTERY_COUNT, 4)
    charge_rate = config.get(CONF_CHARGE_RATE, DEFAULT_CHARGE_RATE)
    entity_patterns = config.get(CONF_ENTITY_PATTERNS)
    scale_factor = config.get(CONF_SCALE_FACTOR, DEFAULT_SCALE_FACTOR)
    manual_entities = config.get(CONF_MANUAL_ENTITIES)
    startup_delay = config.get(CONF_STARTUP_DELAY, 0)
    
    _LOGGER.info(f"Setting up battery tracker with battery_count={battery_count}, " 
                 f"charge_rate={charge_rate}, scale_factor={scale_factor}")
    
    # Add a delay if requested
    if startup_delay > 0:
        _LOGGER.info(f"Waiting {startup_delay} seconds for other integrations to start")
        await asyncio.sleep(startup_delay)
        _LOGGER.info("Startup delay completed")
    
    # Create a coordinator for the tracker
    coordinator = BatteryEnergyCoordinator(
        hass, 
        battery_count, 
        charge_rate, 
        entity_patterns,
        scale_factor,
        manual_entities
    )
    
    # Wait for first refresh
    await coordinator.async_refresh()
    
    entities = []
    
    # Add the tracker entities
    entities.extend([
        TotalDischargeEnergySensor(coordinator),
        TotalChargeEnergySensor(coordinator),
        EnergySinceLastChargeSensor(coordinator),
        EstimatedChargeTimeSensor(coordinator),
        ChargeStatusSensor(coordinator),
        DiagnosticSensor(coordinator)
    ])
    
    async_add_entities(entities)


class BatteryEnergySensor(CoordinatorEntity, SensorEntity):
    """Base class for battery energy sensors."""
    
    def __init__(self, coordinator: BatteryEnergyCoordinator):
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
    """Sensor to track total discharged energy with rollover handling."""
    
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
        return round(self.coordinator.data["total_discharge_kwh"], 2)


class TotalChargeEnergySensor(BatteryEnergySensor):
    """Sensor to track total charged energy with rollover handling."""
    
    _attr_name = "Total Charge Energy"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:battery-plus-outline"
    
    @property
    def unique_id(self):
        """Return unique ID for the sensor."""
        return f"{DOMAIN}_total_charge_energy"
        
    @property
    def native_value(self):
        """Return the total charge energy."""
        return round(self.coordinator.data["total_charge_kwh"], 2)


class EnergySinceLastChargeSensor(BatteryEnergySensor):
    """Sensor to track energy used since last charge."""
    
    _attr_name = "Energy Since Last Charge"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_icon = "mdi:battery-charging-low"
    
    @property
    def unique_id(self):
        """Return unique ID for the sensor."""
        return f"{DOMAIN}_energy_since_last_charge"
        
    @property
    def native_value(self):
        """Return energy used since last charge."""
        return round(self.coordinator.data["energy_since_last_charge"], 2)
    
    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            ATTR_LAST_CHARGE_COMPLETED: self.coordinator.data.get("last_charge_completed"),
            ATTR_CHARGE_DURATION: round(self.coordinator.data.get("last_charge_duration", 0), 2) if self.coordinator.data.get("last_charge_duration") else None,
        }


class EstimatedChargeTimeSensor(BatteryEnergySensor):
    """Sensor to estimate charge time needed."""
    
    _attr_name = "Estimated Charge Time"
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_device_class = None  # No suitable device class
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:clock-outline"
    
    @property
    def unique_id(self):
        """Return unique ID for the sensor."""
        return f"{DOMAIN}_estimated_charge_time"
        
    @property
    def native_value(self):
        """Return estimated time to recharge."""
        estimate = self.coordinator.data.get("estimated_charge_time")
        if estimate is not None:
            return round(estimate, 2)
        return None
    
    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        estimate = self.coordinator.data.get("estimated_charge_time")
        if estimate is not None:
            hours = int(estimate)
            minutes = int((estimate - hours) * 60)
            
            return {
                "hours": hours,
                "minutes": minutes,
                "friendly_format": f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m",
                ATTR_ENERGY_SINCE_LAST_CHARGE: round(self.coordinator.data.get("energy_since_last_charge", 0), 2),
            }
        return {ATTR_ENERGY_SINCE_LAST_CHARGE: 0}


class ChargeStatusSensor(BatteryEnergySensor):
    """Sensor to track battery charging status."""
    
    _attr_name = "Charge Status"
    _attr_icon = "mdi:battery-charging"
    
    @property
    def unique_id(self):
        """Return unique ID for the sensor."""
        return f"{DOMAIN}_charge_status"
        
    @property
    def native_value(self):
        """Return charging status."""
        return self.coordinator.get_charge_status()
    
    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        attrs = {
            "is_charging": self.coordinator.data.get("is_charging", False),
        }
        
        charge_start_time = self.coordinator.data.get("charge_start_time")
        if charge_start_time:
            attrs["charge_start_time"] = charge_start_time
            
            # Calculate elapsed time
            elapsed_seconds = (dt_util.utcnow() - charge_start_time).total_seconds()
            attrs["elapsed_minutes"] = round(elapsed_seconds / 60, 1)
            
        if self.coordinator.data.get("last_charge_completed"):
            attrs["last_charge_completed"] = self.coordinator.data.get("last_charge_completed")
            
        return attrs


class DiagnosticSensor(BatteryEnergySensor):
    """Sensor that provides diagnostic information about the battery tracker."""
    
    _attr_name = "Energy Tracker Diagnostics"
    _attr_icon = "mdi:alert-circle-check"
    
    @property
    def unique_id(self):
        """Return unique ID for the sensor."""
        return f"{DOMAIN}_diagnostics"
        
    @property
    def native_value(self):
        """Return a simple status."""
        diagnostics = self.coordinator.data.get("diagnostics", {})
        battery_entities = diagnostics.get("battery_entities", {})
        
        # Count how many battery entities are found
        count = len(battery_entities)
        
        if count == 0:
            return "No battery entities found"
        elif count < self.coordinator.battery_count:
            return f"Found {count}/{self.coordinator.battery_count} batteries"
        else:
            # Check if all entities are available
            all_available = True
            for battery_data in battery_entities.values():
                for entity_data in battery_data.values():
                    if not entity_data.get("available", False):
                        all_available = False
                        break
                if not all_available:
                    break
                    
            if all_available:
                return "All battery entities found and available"
            else:
                return "All battery entities found but some unavailable"
    
    @property
    def extra_state_attributes(self):
        """Return diagnostic information."""
        diagnostics = self.coordinator.data.get("diagnostics", {})
        tracker_state = diagnostics.get("tracker_state", {})
        
        return {
            "total_discharge_kwh": round(tracker_state.get("total_discharge", 0), 2),
            "total_charge_kwh": round(tracker_state.get("total_charge", 0), 2),
            "energy_since_last_charge": round(tracker_state.get("energy_since_last_charge", 0), 2),
            "is_charging": tracker_state.get("is_charging", False),
            "battery_count": self.coordinator.battery_count,
            "detected_entities": diagnostics.get("battery_entities", {}),
            "retry_count": self.coordinator._retry_count,
        }