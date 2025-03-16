"""Services for the Battery Energy Tracker integration."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_RESET_COUNTERS,
    SERVICE_RESET_ENERGY_SINCE_CHARGE,
    SERVICE_SET_CHARGE_STATE,
    SERVICE_ADJUST_COUNTERS,
    ATTR_IS_CHARGING,
    ATTR_DISCHARGE_ADJUSTMENT,
    ATTR_CHARGE_ADJUSTMENT,
)

_LOGGER = logging.getLogger(__name__)

# Service schemas
RESET_COUNTERS_SCHEMA = vol.Schema({})

RESET_ENERGY_SINCE_CHARGE_SCHEMA = vol.Schema({})

SET_CHARGE_STATE_SCHEMA = vol.Schema({
    vol.Required(ATTR_IS_CHARGING): cv.boolean,
})

ADJUST_COUNTERS_SCHEMA = vol.Schema({
    vol.Optional(ATTR_DISCHARGE_ADJUSTMENT): vol.Coerce(float),
    vol.Optional(ATTR_CHARGE_ADJUSTMENT): vol.Coerce(float),
})

async def async_register_services(hass: HomeAssistant) -> None:
    """Register services for the Battery Energy Tracker integration."""
    _LOGGER.info("Registering Battery Energy Tracker services")
    
    if DOMAIN not in hass.data:
        _LOGGER.error("Cannot register services, coordinator not found in hass.data")
        return
        
    coordinator = hass.data[DOMAIN]
    
    async def handle_reset_counters(call: ServiceCall) -> None:
        """Handle the reset_counters service call."""
        _LOGGER.info("Service call: reset_counters")
        await coordinator.reset_counters()
    
    async def handle_reset_energy_since_charge(call: ServiceCall) -> None:
        """Handle the reset_energy_since_charge service call."""
        _LOGGER.info("Service call: reset_energy_since_charge")
        await coordinator.reset_energy_since_charge()
    
    async def handle_set_charge_state(call: ServiceCall) -> None:
        """Handle the set_charge_state service call."""
        is_charging = call.data[ATTR_IS_CHARGING]
        _LOGGER.info(f"Service call: set_charge_state with is_charging={is_charging}")
        await coordinator.set_charge_state(is_charging)
    
    async def handle_adjust_counters(call: ServiceCall) -> None:
        """Handle the adjust_counters service call."""
        discharge_adjustment = call.data.get(ATTR_DISCHARGE_ADJUSTMENT)
        charge_adjustment = call.data.get(ATTR_CHARGE_ADJUSTMENT)
        
        _LOGGER.info(f"Service call: adjust_counters with discharge_adjustment={discharge_adjustment}, charge_adjustment={charge_adjustment}")
        
        await coordinator.adjust_counters(
            discharge_adjustment=discharge_adjustment,
            charge_adjustment=charge_adjustment
        )
    
    # Register services
    hass.services.async_register(
        DOMAIN, 
        SERVICE_RESET_COUNTERS, 
        handle_reset_counters,
        schema=RESET_COUNTERS_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, 
        SERVICE_RESET_ENERGY_SINCE_CHARGE, 
        handle_reset_energy_since_charge,
        schema=RESET_ENERGY_SINCE_CHARGE_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, 
        SERVICE_SET_CHARGE_STATE, 
        handle_set_charge_state,
        schema=SET_CHARGE_STATE_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, 
        SERVICE_ADJUST_COUNTERS, 
        handle_adjust_counters,
        schema=ADJUST_COUNTERS_SCHEMA
    )
    
    _LOGGER.info("Battery Energy Tracker services registered successfully")

async def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister services for the Battery Energy Tracker integration."""
    _LOGGER.info("Unregistering Battery Energy Tracker services")
    
    # Unregister all services
    for service in [
        SERVICE_RESET_COUNTERS,
        SERVICE_RESET_ENERGY_SINCE_CHARGE,
        SERVICE_SET_CHARGE_STATE,
        SERVICE_ADJUST_COUNTERS,
    ]:
        hass.services.async_remove(DOMAIN, service)