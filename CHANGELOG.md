# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## v0.1.2 - 2025-12-15

### Added
- Regex-based filtering of MeshCom ACK messages addressed to the configured `my_call`.
- ACK messages in the format `<my_call>:ack<id>` are now ignored to prevent self-triggered events.
- Improved message filtering to reduce internal MeshCom protocol noise.

### Changed
- Time beacon messages (`{CET}...`, `{CEST}...`) are now completely ignored:
  - No sensor updates
  - No `meshcom_message` events
- Message parsing logic was refined to only process meaningful, human-readable text messages.
- Reduced event and sensor noise caused by transport-level MeshCom responses.

### Fixed
- Prevented ACK responses to outgoing messages from appearing as incoming messages.
- Avoided unintended automations triggered by MeshCom acknowledgements.

---

## v0.1.1 - 2025-12-15

### Added
- Home Assistant service `meshcom.send_message` to send text messages into the MeshCom network.
- Bidirectional MeshCom support (send + receive).
- `my_call` is now included in every `meshcom_message` event payload.
- Enables automations to dynamically reference the configured callsign.
- Example PING responder automation without hardcoded callsigns.
- README documentation updated accordingly.

### Changed
- Integration description updated to reflect bidirectional messaging support.

---

## v0.1.0 - 2025-12-15

### Added
- Initial public release of the Home-Assistant MeshCom Integration.
- Direct UDP reception of MeshCom messages without external proxies.
- UI-based configuration using Home Assistant config flow.
- Filtering of incoming messages by destination callsign and groups.
- Support for MeshCom group addressing (including `*` wildcard).
- Sensors for:
    - Last message text
    - Source callsign
    - Destination callsign
    - Message ID
    - Timestamp of last valid message
    - Raw JSON payload
- Custom Home Assistant event `meshcom_message`.
- Multilingual UI support (English and German).

### Notes
- This version supports receiving MeshCom messages only.