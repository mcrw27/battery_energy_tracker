"""Coordinator for the Battery Energy Tracker integration."""
import logging

# Import the main coordinator class
from .coordinator_base import BatteryEnergyCoordinator

# Import methods to attach
from . import charge_state, counter_processor, diagnostics, entity_detector, services

_LOGGER = logging.getLogger(__name__)

# Attach methods to the BatteryEnergyCoordinator class
BatteryEnergyCoordinator.auto_detect_entities = entity_detector.auto_detect_entities
BatteryEnergyCoordinator._update_counters = counter_processor._update_counters
BatteryEnergyCoordinator._process_counter_value = counter_processor._process_counter_value
BatteryEnergyCoordinator._update_charging_status = charge_state._update_charging_status
BatteryEnergyCoordinator.diagnostic_check = diagnostics.diagnostic_check
BatteryEnergyCoordinator.reset_counters = services.reset_counters
BatteryEnergyCoordinator.reset_energy_since_charge = services.reset_energy_since_charge
BatteryEnergyCoordinator.set_charge_state = services.set_charge_state
BatteryEnergyCoordinator.adjust_counters = services.adjust_counters