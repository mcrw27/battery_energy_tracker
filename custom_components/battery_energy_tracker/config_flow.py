"""Config flow for Battery Energy Tracker integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv
from homeassistant.data_entry_flow import FlowResult

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
)

_LOGGER = logging.getLogger(__name__)

class BatteryEnergyTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Battery Energy Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input
            try:
                # Since this is a singleton integration (only one instance allowed),
                # check if it's already configured
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                
                # Return the info to be stored in the config entry
                return self.async_create_entry(
                    title="Battery Energy Tracker",
                    data=user_input,
                )
            except Exception as e:
                _LOGGER.exception("Unexpected exception during setup: %s", e)
                errors["base"] = "unknown"

        # Form schema
        schema = vol.Schema(
            {
                vol.Required(CONF_BATTERY_COUNT, default=4): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=16)
                ),
                vol.Required(CONF_CHARGE_RATE, default=DEFAULT_CHARGE_RATE): vol.All(
                    vol.Coerce(float), vol.Range(min=100, max=10000)
                ),
                vol.Optional(CONF_STARTUP_DELAY, default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=300)
                ),
                vol.Optional(CONF_SCALE_FACTOR, default=DEFAULT_SCALE_FACTOR): vol.All(
                    vol.Coerce(float), vol.Range(min=0.001, max=10)
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BatteryEnergyTrackerOptionsFlow(config_entry)


class BatteryEnergyTrackerOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the Battery Energy Tracker integration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        # Don't store the config_entry directly
        self.entry_id = config_entry.entry_id
        self.options = dict(config_entry.options)
        self.data = dict(config_entry.data)

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Update options
            return self.async_create_entry(title="", data=user_input)

        # Prepare form with current values
        options = {**self.data, **self.options}
        
        # Advanced settings form
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_BATTERY_COUNT, 
                    default=options.get(CONF_BATTERY_COUNT, 4)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=16)),
                vol.Required(
                    CONF_CHARGE_RATE, 
                    default=options.get(CONF_CHARGE_RATE, DEFAULT_CHARGE_RATE)
                ): vol.All(vol.Coerce(float), vol.Range(min=100, max=10000)),
                vol.Optional(
                    CONF_STARTUP_DELAY, 
                    default=options.get(CONF_STARTUP_DELAY, 0)
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=300)),
                vol.Optional(
                    CONF_SCALE_FACTOR, 
                    default=options.get(CONF_SCALE_FACTOR, DEFAULT_SCALE_FACTOR)
                ): vol.All(vol.Coerce(float), vol.Range(min=0.001, max=10)),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=schema, errors=errors
        )