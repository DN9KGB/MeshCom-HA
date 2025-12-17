from __future__ import annotations

import logging
from typing import Callable

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import DOMAIN, MeshComGateway

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MeshCom sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    gateway: MeshComGateway = data["gateway"]

    entities: list[SensorEntity] = [
        MeshComLastMessageSensor(gateway, entry),
        MeshComSourceSensor(gateway, entry),
        MeshComDestinationSensor(gateway, entry),
        MeshComMessageIdSensor(gateway, entry),
        MeshComTimestampSensor(gateway, entry),
    ]

    async_add_entities(entities)


class MeshComBaseSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, gateway: MeshComGateway, entry: ConfigEntry) -> None:
        self._gateway = gateway
        self._entry = entry
        self._unsub_callback: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        @callback
        async def _handle_update() -> None:
            self.async_write_ha_state()

        self._unsub_callback = self._gateway.register_listener(_handle_update)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_callback is not None:
            self._unsub_callback()
            self._unsub_callback = None


class MeshComLastMessageSensor(MeshComBaseSensor):
    _attr_translation_key = "last_message"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_last_message"

    @property
    def native_value(self) -> str | None:
        return self._gateway.last_message


class MeshComSourceSensor(MeshComBaseSensor):
    _attr_translation_key = "source_callsign"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_source"

    @property
    def native_value(self) -> str | None:
        return self._gateway.last_source


class MeshComDestinationSensor(MeshComBaseSensor):
    _attr_translation_key = "destination_callsign"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_destination"

    @property
    def native_value(self) -> str | None:
        return self._gateway.last_destination


class MeshComMessageIdSensor(MeshComBaseSensor):
    _attr_translation_key = "message_id"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_msg_id"

    @property
    def native_value(self) -> str | None:
        return self._gateway.last_message_id




class MeshComTimestampSensor(MeshComBaseSensor):
    _attr_translation_key = "timestamp"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_timestamp"

    @property
    def native_value(self):
        if self._gateway.last_timestamp is None:
            return None

        dt = dt_util.parse_datetime(self._gateway.last_timestamp)
        return dt
