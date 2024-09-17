import datetime
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_NAME, STATE_OFF, STATE_ON
)
import voluptuous as vol

DOMAIN = "casovni_bloki"

# Configuration schema for YAML
CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME, default="Casovni bloki"): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up sensor"""
    name = config.get(CONF_NAME)
    async_add_entities([CasovniBlokiSensor(hass, name)], True)


class CasovniBlokiSensor(SensorEntity):
    """Representation of current time block."""

    def __init__(self, hass, name):
        """Initialize the sensor."""
        self.hass = hass
        self._name = name
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the time block."""
        return self._state

    def update(self):
        """Fetch the latest power limit."""
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_day = datetime.datetime.now().strftime("%A")
        is_holiday = self.hass.states.get("binary_sensor.workday").state == STATE_OFF

        if is_holiday:
            self._state = self.get_holiday_limit(current_time)
        else:
            self._state = self.get_regular_limit(current_time, current_day)

    def get_holiday_limit(self, current_time):
        """Return the holiday block limits based on the time."""
        if '00:00' <= current_time < '06:00':
            return 6
        elif '06:00' <= current_time < '12:00':
            return 8
        elif '12:00' <= current_time < '18:00':
            return 12
        elif '18:00' <= current_time < '21:00':
            return 6
        elif '21:00' <= current_time < '23:59':
            return 5

    def get_regular_limit(self, current_time, current_day):
        """Return the regular block limits based on the time and day."""
        if current_day in ['Monday', 'Tuesday', 'Wednesday']:
            if '00:00' <= current_time < '06:00':
                return 5
            elif '06:00' <= current_time < '12:00':
                return 7
            elif '12:00' <= current_time < '18:00':
                return 10
            elif '18:00' <= current_time < '21:00':
                return 5
            elif '21:00' <= current_time < '23:59':
                return 4
        elif current_day in ['Thursday', 'Friday']:
            if '00:00' <= current_time < '06:00':
                return 6
            elif '06:00' <= current_time < '12:00':
                return 8
            elif '12:00' <= current_time < '18:00':
                return 11
            elif '18:00' <= current_time < '21:00':
                return 5
            elif '21:00' <= current_time < '23:59':
                return 4
        else:
            return 5