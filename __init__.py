from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Awaitable, Callable
from datetime import datetime, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType

DOMAIN = "meshcom"
PLATFORMS: list[str] = ["sensor"]

_LOGGER = logging.getLogger(__name__)


class MeshComGateway(asyncio.DatagramProtocol):
    """UDP gateway handling MeshCom packets."""

    def __init__(self, hass: HomeAssistant, my_call: str | None, groups: list[str]) -> None:
        """Initialize the gateway."""
        self.hass = hass

        # Normalize calls and groups to upper-case for comparison
        self.my_call: str | None = my_call.upper() if my_call else None
        self.groups: list[str] = [g.upper() for g in groups]

        self.transport: asyncio.DatagramTransport | None = None

        # Listeners (entities) that want to be notified on updates
        self._listeners: list[Callable[[], Awaitable[None]] | Callable[[], None]] = []

        # Latest values for sensor entities
        self.last_message: str | None = None
        self.last_source: str | None = None
        self.last_destination: str | None = None
        self.last_message_id: str | None = None
        self.last_timestamp: str | None = None
        self.last_raw_json: dict[str, Any] | None = None
        self.last_raw_bytes: bytes | None = None

    # UDP CONNECTION EVENTS
    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when the UDP socket is created."""
        self.transport = transport  # type: ignore[assignment]
        _LOGGER.info("MeshCom UDP gateway started")

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when the UDP socket is closed."""
        _LOGGER.info("MeshCom UDP gateway stopped: %s", exc)

    # UDP PACKET HANDLER
    def datagram_received(self, data: bytes, addr) -> None:
        """Handle incoming UDP MeshCom datagram."""
        _LOGGER.debug("Received UDP packet from %s: %r", addr, data)
        self.last_raw_bytes = data

        # Decode payload (MeshCom-Client uses UTF-8 JSON)
        try:
            decoded = data.decode("utf-8", errors="ignore").strip()
        except Exception:
            _LOGGER.warning("Failed to decode UDP packet as UTF-8")
            return

        if not decoded:
            _LOGGER.debug("Empty UDP payload received from %s", addr)
            return

        # Parse JSON object
        try:
            payload = json.loads(decoded)
        except Exception as err:
            _LOGGER.warning("Invalid JSON from %s: %s", addr, err)
            _LOGGER.debug("Offending payload: %s", decoded)
            return

        if not isinstance(payload, dict):
            _LOGGER.warning("MeshCom payload is not a JSON object: %r", payload)
            return

        # Extract basic fields
        raw_src = payload.get("src", "Unknown")
        raw_dst = payload.get("dst", "*")
        src_call = str(raw_src).upper()
        dst_call = str(raw_dst).upper()

        raw_msg_text = str(payload.get("msg", ""))

        # Ignore messages that have no text or empty msg field
        if raw_msg_text is None or raw_msg_text.strip() == "":
            _LOGGER.debug("Ignoring message without text content: %s", payload)
            return

        message_id = str(payload.get("msg_id", ""))

        # DESTINATION FILTER:
        # Only process messages where dst matches my_call or one of the groups.
        allowed = False

        if self.my_call and dst_call == self.my_call:
            allowed = True
        elif dst_call in self.groups:
            allowed = True

        if not allowed:
            _LOGGER.debug(
                "Ignoring message not addressed to me (%s) or my groups (%s): dst=%s",
                self.my_call,
                self.groups,
                dst_call,
            )
            return


        # Strip APRS-style message number suffix: "text{1234"
        clean_msg_text = re.sub(r"\{\d{1,4}$", "", raw_msg_text)

        # Detect time beacons like "{CET}..." / "{CEST}..."
        is_time_beacon = clean_msg_text.startswith("{CET}") or clean_msg_text.startswith(
            "{CEST}"
        )


        # Update internal state for entities
        self.last_source = src_call
        self.last_destination = dst_call
        self.last_message_id = message_id
        self.last_timestamp = datetime.now(timezone.utc).isoformat()
        self.last_raw_json = payload


        if is_time_beacon:
            _LOGGER.debug("Time beacon received from %s: %s", src_call, clean_msg_text)
            # Do not treat as "last_message"
            self.last_message = None
        else:
            self.last_message = clean_msg_text.replace('"', "'")


        # Fire custom event meshcom_message
        event_data: dict[str, Any] = {
            "src": src_call,
            "dst": dst_call,
            "msg": clean_msg_text,
            "raw_msg": raw_msg_text,
            "msg_id": message_id,
            "is_time_beacon": is_time_beacon,
            "src_type": payload.get("src_type"),
            "firmware": payload.get("firmware"),
            "fw_sub": payload.get("fw_sub"),
            "raw": payload,
        }

        _LOGGER.debug("Firing event meshcom_message: %s", event_data)
        self.hass.bus.fire("meshcom_message", event_data)


        # Notify all registered listeners (sensor entities)
        for listener in list(self._listeners):
            self.hass.add_job(listener)

    # ENTITY LISTENER MANAGEMENT
    @callback
    def register_listener(
        self, listener: Callable[[], Awaitable[None]] | Callable[[], None]
    ) -> Callable[[], None]:
        """Register a callback that is called when new data is available."""
        self._listeners.append(listener)

        def _remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _remove


# INTEGRATION SETUP


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up MeshCom from configuration.yaml (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MeshCom from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    bind_ip = entry.data.get("bind_ip", "0.0.0.0")
    port = entry.data.get("port", 1799)
    my_call = entry.data.get("my_call")
    groups_raw = entry.data.get("groups", "")
    
    groups = [g.strip() for g in str(groups_raw).split(",") if g.strip()]

    loop = asyncio.get_running_loop()

    gateway = MeshComGateway(hass, my_call, groups)

    transport, _protocol = await loop.create_datagram_endpoint(
        lambda: gateway,
        local_addr=(bind_ip, port),
    )

    _LOGGER.info(
        "MeshCom UDP listener bound to %s:%s (my_call=%s, groups=%s)",
        bind_ip,
        port,
        gateway.my_call,
        gateway.groups,
    )

    hass.data[DOMAIN][entry.entry_id] = {
        "gateway": gateway,
        "transport": transport,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a MeshCom config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    data = hass.data[DOMAIN].pop(entry.entry_id, {})
    transport: asyncio.DatagramTransport | None = data.get("transport")
    if transport is not None:
        transport.close()

    return unload_ok
