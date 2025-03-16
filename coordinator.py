"""Main coordinator for the Battery Energy Tracker integration."""
import logging

# Import the main coordinator class
from .coordinator import BatteryEnergyCoordinator

# Import the various methods we'll attach to the coordinator
from .coordinator import counter_processor, entity_detection, charge_state, diagnostics, services

_LOGGER = logging.getLogger(__name__)

# Attach the methods to the BatteryEnergyCoordinator class
BatteryEnergyCoordinator.auto_detect_entities = entity_detection.auto_detect_entities
BatteryEnergyCoordinator._update_counters = counter_processor._update_counters
BatteryEnergyCoordinator._process_counter_value = counter_processor._process_counter_value
BatteryEnergyCoordinator._update_charging_status = charge_state._update_charging_status
BatteryEnergyCoordinator.diagnostic_check = diagnostics.diagnostic_check
BatteryEnergyCoordinator.reset_counters = services.reset_counters
BatteryEnergyCoordinator.reset_energy_since_charge = services.reset_energy_since_charge
BatteryEnergyCoordinator.set_charge_state = services.set_charge_state
BatteryEnergyCoordinator.adjust_counters = services.adjust_counters