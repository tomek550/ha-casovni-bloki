import datetime
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_NAME, STATE_OFF, STATE_ON
)
from .const import DOMAIN
import voluptuous as vol
from enum import Enum
from .holidays import HOLIDAYS


DOMAIN = "casovni_bloki"


class LowSeason(Enum):
    HIGH = 3
    MID = 4
    LOW = 5
class MidSeason(Enum):
    HIGH = 2
    MID = 3
    LOW = 4
class HighSeason(Enum):
    HIGH = 1
    MID = 2
    LOW = 3


# Configuration schema for YAML
CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME, default="Casovni blok"): cv.string,
})


async def async_reload_entry(hass, config_entry):    
    sensor_unload_ok = await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")

    if sensor_unload_ok:
        active_entities = hass.states.async_entity_ids()
        unload_ok = await hass.config_entries.async_unload(config_entry.entry_id)

        if unload_ok:
            await hass.config_entries.async_setup(config_entry.entry_id)
            return True
        else:
            return False
    else:
        return False


async def async_unload_entry(hass, config_entry):
    
    # Log active entities before unload
    active_entities = hass.states.async_entity_ids()

    # Unload the sensor platform
    sensor_unload_ok = await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")

    if sensor_unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id, None)
        return True
    else:
        return False

    return unload_ok

async def async_setup_entry(hass, config_entry, async_add_entities):
    hass.data[DOMAIN][config_entry.entry_id] = {
        "block_1_limit": config_entry.data.get("block_1_limit", 5.5),
        "block_2_limit": config_entry.data.get("block_2_limit", 7.3),
        "block_3_limit": config_entry.data.get("block_3_limit", 9.1),
        "block_4_limit": config_entry.data.get("block_4_limit", 9.1),
        "block_5_limit": config_entry.data.get("block_5_limit", 9.1),
    }

    name = config_entry.data.get("name", "Casovni Bloki")
    casovni_blok_sensor = CasovniBlokSensor(hass, name, config_entry.entry_id)
    casovni_blok_limit_sensor = CasovniBlokLimitSensor(hass, f"{name} Limit", casovni_blok_sensor, config_entry.entry_id)
    casovni_blok_level_sensor = CasovniBlokLevelSensor(hass, f"{name} Level", config_entry.entry_id)

    async_add_entities([casovni_blok_sensor, casovni_blok_limit_sensor, casovni_blok_level_sensor], True)

    # config_entry.async_on_unload(
    #     config_entry.add_update_listener(async_reload_entry)
    # )

class CasovniBlokSensor(SensorEntity):
    """Representation of current time block."""

    def __init__(self, hass, name, entry_id):
        """Initialize the sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._name = name
        self._state = None
        self._unsubscribe_listener = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{self._entry_id}_casovni_blok"

    @property
    def state(self):
        """Return the time block."""
        return self._state

    async def async_update(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_day = datetime.datetime.now().strftime("%A")
        current_month = datetime.datetime.now().month

        self._state = self.get_block(current_time, current_day, current_month)

    def get_block(self, current_time, current_day, current_month):
        """Return the time block based on the time and day."""
        tarifs = LowSeason;

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        lowSeason = True;
        if current_month in [11, 12, 1, 2]:
            lowSeason = False;

        weekday = False;
        if current_day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] and current_date not in HOLIDAYS:
            weekday = True;
        
        if lowSeason and not weekday:
            tarifs = LowSeason
        elif not lowSeason and weekday:
            tarifs = HighSeason
        else:
            tarifs = MidSeason

        if '00:00' <= current_time < '06:00':
            return tarifs.LOW.value
        elif '06:00' <= current_time < '07:00':
            return tarifs.MID.value
        elif '07:00' <= current_time < '14:00':
            return tarifs.HIGH.value
        elif '14:00' <= current_time < '16:00':
            return tarifs.MID.value
        elif '16:00' <= current_time < '20:00':
            return tarifs.HIGH.value
        elif '20:00' <= current_time < '22:00':
            return tarifs.MID.value
        else:
            return tarifs.LOW.value

            
class CasovniBlokLimitSensor(SensorEntity):
    """Representation of current time block."""

    def __init__(self, hass, name, casovni_blok_sensor, entry_id):
        """Initialize the sensor."""
        self.hass = hass
        self._name = name
        self._state = None
        self.casovni_blok_sensor = casovni_blok_sensor
        self._entry_id = entry_id

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "kW"

    @property
    def unique_id(self):
        """Return a unique ID for this limit sensor."""
        return f"{self._entry_id}_casovni_blok_limit"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the time block.""" 
        return self._state

    async def async_update(self):
        """Fetch the latest power limit asynchronously."""
        time_block = self.casovni_blok_sensor.state

        limits_map  = {
            1: self.hass.data[DOMAIN][self._entry_id]["block_1_limit"],
            2: self.hass.data[DOMAIN][self._entry_id]["block_2_limit"],
            3: self.hass.data[DOMAIN][self._entry_id]["block_3_limit"],
            4: self.hass.data[DOMAIN][self._entry_id]["block_4_limit"],
            5: self.hass.data[DOMAIN][self._entry_id]["block_5_limit"],
        }

        if time_block in limits_map:
            self._state = limits_map[time_block]
        else:
            self._state = None 


            
class CasovniBlokLevelSensor(SensorEntity):
    """Representation of current time block."""

    def __init__(self, hass, name, entry_id):
        """Initialize the sensor."""
        self.hass = hass
        self._name = name
        self._entry_id = entry_id

    @property
    def unique_id(self):
        """Return a unique ID for this level sensor."""
        return f"{self._entry_id}_casovni_blok_level"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the time block.""" 
        return self._state

    async def async_update(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        if '00:00' <= current_time < '06:00':
            self._state = "LOW"
        elif '06:00' <= current_time < '07:00':
            self._state = "MID"
        elif '07:00' <= current_time < '14:00':
            self._state = "HIGH"
        elif '14:00' <= current_time < '16:00':
            self._state = "MID"
        elif '16:00' <= current_time < '20:00':
            self._state = "HIGH"
        elif '20:00' <= current_time < '22:00':
            self._state = "MID"
        else:
            self._state = "LOW"
