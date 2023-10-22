from __future__ import annotations

import logging
import enum

from datetime import datetime

from homeassistant.components.sensor import (
    DOMAIN as ENTITY_DOMAIN,
    SensorStateClass,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.util import dt
from homeassistant.const import *

# try:
#     # hass 2023.9
#     from homeassistant.components.weather import WeatherEntityFeature
# except (ModuleNotFoundError, ImportError):
#     WeatherEntityFeature = None

from . import TianqiClient, async_add_setuper, HTTP_REFERER

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        device_class=SensorDeviceClass.AQI,
        state_class=SensorStateClass.MEASUREMENT,
        key="aqi",
        name="AQI",
        icon="mdi:lung"
    ),
)


def setuper(add_entities):
    def setup(client: TianqiClient):
        entities = [TianqiSensor(client, description) for description in SENSOR_TYPES]
        # for e in entities:
        #     if not e.added:
        #         add_entities([e])

        add_entities(entities)
        # if not (entity := client.entities.get(ENTITY_DOMAIN)):
        #     entity = SensorEntity(client)
        # if not entity.added:
        #     add_entities([entity])
    return setup

# async def async_setup_entry(hass, config_entry, async_add_entities):
#     await async_add_setuper(hass, config_entry, ENTITY_DOMAIN, setuper(async_add_entities))


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    await async_add_setuper(hass, config or discovery_info, ENTITY_DOMAIN, setuper(async_add_entities))
   


class TianqiSensor(SensorEntity):
    added = False
    _attr_should_poll = False

    def __init__(self, client: TianqiClient, description):
        self.entity_description = description
        self._attr_name = description.name
        self.client = client
        self.hass = client.hass

        station = client.station
        code = station.area_code or station.area_name or self.hass.config.location_name
        self.entity_id = f'{ENTITY_DOMAIN}.{code}.{description.key}'

    # async def async_added_to_hass(self):
    #     self.added = True
    #     self.client.entities[ENTITY_DOMAIN] = self

    #     await super().async_added_to_hass()
    #     await self.update_from_client()

    # async def update_from_client(self):
    #     dat = self.client.data
    #     dataSK = dat.get('dataSK') or {}

    #     if self.entity_description.key in SK_KEYS:
    #         self._attr_native_value = dataSK.get(self.entity_description.key)

    @property
    def native_value(self):
        dat = self.client.data
        dataSK = dat.get('dataSK') or {}

        if self.entity_description.key == "aqi":
            return dataSK.get(self.entity_description.key)

    @property
    def native_unit_of_measurement(self):
        return self.entity_description.native_unit_of_measurement

