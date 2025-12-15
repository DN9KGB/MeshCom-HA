# Home-Assistant MeshCom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/)
[![Version](https://img.shields.io/github/v/release/DN9KGB/MeshCom-HA?style=for-the-badge)](https://github.com/DN9KGB/MeshCom-HA/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

A native MeshCom integration for Home Assistant that receives UDP packets directly from MeshCom nodes, parses message content, filters by callsign/groups, and exposes structured entities and events to Home Assistant.

This integration enables full automation support for MeshCom messaging without any external proxy or service.

---

## ✨ Features

✔ Direct UDP reception from MeshCom nodes  
✔ Filters messages by **destination callsign** or **groups**  
✔ Only processes **text messages** with non-empty payload  
✔ Provides multiple sensors:  
- Last Message  
- Source Callsign  
- Destination Callsign  
- Message ID  
- Timestamp (device_class: timestamp, auto-localized)  
- Raw JSON  

✔ Fires a custom event: **`meshcom_message`**  
✔ Fully configurable through the UI (no YAML required)  
✔ Supports multilingual UI (English + German)  
✔ HACS compatible  

---

# 🧩 Installation

You can install this integration **via HACS** (recommended) or manually.

---

# 🟦 Install via HACS (Recommended)

### 1. Open HACS → *Integrations*  
### 2. Click the menu (⋮) → **Custom repositories**  
### 3. Add:

```
https://github.com/DN9KGB/MeshCom-HA
```

Category: **Integration**

### 4. Install *Home-Assistant MeshCom Integration*  
### 5. Restart Home Assistant  
### 6. Go to:

**Settings → Devices & Services → Add Integration → “MeshCom”**

No YAML required.

---

# 📁 Manual Installation (Alternative)

1. Download the latest release ZIP from:  
   https://github.com/DN9KGB/MeshCom-HA/releases

2. Extract it into:

```
config/custom_components/meshcom/
```

The directory must look like:

```
custom_components/meshcom/
├── __init__.py
├── manifest.json
├── config_flow.py
├── sensor.py
├── translations/
│   ├── en.json
│   └── de.json
└── logo.png / icon.png
```

3. Restart Home Assistant  
4. Add the integration through the UI

---

# 📡 MeshCom Node Configuration

To send messages into Home Assistant, your MeshCom node must have external UDP output enabled.

Typical MeshCom configuration:

```
--extudpip 192.168.1.10   # IP of your Home Assistant
--extudp on
```

Ensure your node and Home Assistant are on the same network.

---

# ⚙️ Home Assistant Configuration (UI)

When adding the integration, you will see:

### **Bind IP**
The IP address Home Assistant listens on.  
Default: `0.0.0.0` (all interfaces)

### **Port**
UDP port to receive MeshCom packets.  
Default: `1799`

### **My Call**
Your personal MeshCom callsign with ssid.  
Only messages addressed to this callsign or matching one of your groups will be processed.

### **Groups**
Comma-separated list of allowed group destinations.  
Examples:

```
*,10,262
```

`*` means: receive all broadcast messages.
`10` means: WW-GE (worldwide German)
`262` means: Germany

List of groups: https://icssw.org/en/meshcom-grc-gruppen/

---

# 🧾 Provided Sensors

| Entity ID | Description |
|-----------|-------------|
| `sensor.meshcom_last_message` | Last received text message |
| `sensor.meshcom_source_callsign` | Message source (src) |
| `sensor.meshcom_destination_callsign` | Message destination (dst) |
| `sensor.meshcom_message_id` | Message ID |
| `sensor.meshcom_last_timestamp` | Timestamp of last valid message |
| `sensor.meshcom_raw_json` | Full parsed MeshCom JSON payload |

Only messages **with non-empty text** and matching the call/group filter are processed.

---

# 🔔 Event: `meshcom_message`

Every processed message emits a Home Assistant event:

```yaml
event_type: meshcom_message
data:
  src: D1XYZ-11
  dst: D1ABC-12
  msg: "Hello World"
  msg_id: "EF27D069"
  is_time_beacon: false
  firmware: 35
  fw_sub: "h"
  raw: {...}
```

Useful for advanced automations.

---

# ⚡ Example Automation

```yaml
alias: Notify on MeshCom Message
trigger:
  - platform: event
    event_type: meshcom_message

action:
  - service: notify.mobile_app_phone
    data:
      message: >
        MeshCom: {{ trigger.event.data.src }} → {{ trigger.event.data.dst }}:
        {{ trigger.event.data.msg }}
```

---

# 🌍 Localization (i18n)

The integration includes translations for:

- English  
- German  

Home Assistant automatically selects the correct language.

---

# 🛠 Troubleshooting

### ❗ The integration cannot be added through the UI  
Ensure `manifest.json` contains:

```json
"config_flow": true
```

### ❗ No messages received  
Check your node:

```
--extudpip <correct HA IP>
--extudp on
```

### ❗ Empty messages are ignored  
This is intentional — only messages containing text are processed.

---

# 📦 Development

Enable debug output:

```yaml
logger:
  logs:
    custom_components.meshcom: debug
```

Pull requests are welcome!

---

# 📝 License

MIT License — see `LICENSE`.

---

# 👤 Author

D1ABC  
GitHub: https://github.com/DN9KGB/MeshCom-HA
