"""Service methods for the Battery Energy Tracker integration."""
import logging
from typing import Optional
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

# Note: These functions will be attached to a class, so we use 'self' parameter
async def reset_counters(self):
    """Reset all counters to zero."""
    _LOGGER.info("Resetting all energy counters")
    self.total_discharge_counter = 0
    self.total_charge_counter = 0
    self.energy_since_last_charge_counter = 0
    self.total_discharge_kwh = 0.0
    self.total_charge_kwh = 0.0
    self.energy_since_last_charge = 0.0
    await self.async_refresh()
    
async def reset_energy_since_charge(self):
    """Reset energy since last charge counter."""
    _LOGGER.info("Resetting energy since last charge counter")
    self.energy_since_last_charge_counter = 0
    self.energy_since_last_charge = 0.0
    await self.async_refresh()
    
async def set_charge_state(self, is_charging: bool):
    """Manually set the charging state."""
    _LOGGER.info(f"Manually setting charge state to: {is_charging}")
    
    was_charging = self.is_charging
    self.is_charging = is_charging
    
    # Handle state transitions
    if is_charging and not was_charging:
        # Charging just started
        self.charge_start_time = dt_util.utcnow()
        _LOGGER.info("Charging started (manual) at %s", self.charge_start_time)
        
    elif not is_charging and was_charging:
        # Charging just ended
        charge_end_time = dt_util.utcnow()
        self.last_charge_completed = charge_end_time
        
        # Calculate charge duration
        if self.charge_start_time:
            self.last_charge_duration = (charge_end_time - self.charge_start_time).total_seconds() / 3600  # hours
            _LOGGER.info("Charging completed (manual). Duration: %.2f hours", self.last_charge_duration)
        
        self.charge_start_time = None
        
async def adjust_counters(self, discharge_adjustment: Optional[float] = None, charge_adjustment: Optional[float] = None):
    """Adjust the counter values."""
    if discharge_adjustment is not None:
        self.total_discharge_counter += discharge_adjustment
        # Recalculate kWh value
        self.total_discharge_kwh = self.total_discharge_counter * 0.001
        _LOGGER.info(f"Adjusted total discharge counter to {self.total_discharge_counter} ({self.total_discharge_kwh:.2f} kWh)")
        
    if charge_adjustment is not None:
        self.total_charge_counter += charge_adjustment
        # Recalculate kWh value
        self.total_charge_kwh = self.total_charge_counter * 0.001
        _LOGGER.info(f"Adjusted total charge counter to {self.total_charge_counter} ({self.total_charge_kwh:.2f} kWh)")
        
    await self.async_refresh()