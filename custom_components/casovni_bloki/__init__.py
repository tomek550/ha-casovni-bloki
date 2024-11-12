from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Casovni Bloki from a config entry."""

    # Retrieve the configured limits for each time block
    block_1_limit = entry.data.get("block_1_limit", 5)
    block_2_limit = entry.data.get("block_2_limit", 7)
    block_3_limit = entry.data.get("block_3_limit", 10)
    block_4_limit = entry.data.get("block_4_limit", 5)
    block_5_limit = entry.data.get("block_5_limit", 4)

    # Pass the limits to the sensor
    hass.data[DOMAIN] = {
        "block_1_limit": block_1_limit,
        "block_2_limit": block_2_limit,
        "block_3_limit": block_3_limit,
        "block_4_limit": block_4_limit,
        "block_5_limit": block_5_limit,
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True
