"""The Battery Energy Tracker integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define the platforms we support
PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Battery Energy Tracker component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Battery Energy Tracker from a config entry."""
    # Import coordinator to ensure methods are attached
    from .coordinator_base import BatteryEnergyCoordinator
    from . import coordinator
    
    # Get configuration
    config = entry.data
    
    # Create coordinator instance
    battery_tracker = BatteryEnergyCoordinator(
        hass,
        config.get("battery_count", 4),
        config.get("charge_rate", 1500),
        config.get("entity_patterns"),
        config.get("scale_factor", 0.1),
        config.get("manual_entities"),
    )
    
    # Initialize coordinator
    await battery_tracker.async_config_entry_first_refresh()
    
    # Store for later use
    hass.data[DOMAIN][entry.entry_id] = battery_tracker
    
    # Set up all supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services later
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok