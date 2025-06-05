# Trannergy Inverter Home Assistant Custom Integration

This integration integrates the Trannergy solar inverter into Home Assistant.

## Installation

Clone this repositiory in config/custom_components.

Restart Home Assistant

## Configuration

Add integration and fill in the needed fields:

- Name
    - Leave default or change if needed
- IP address of the inverter
    - Configure wifi if needed: https://www.apsolar.nl/wp-content/uploads/trannergy_wifi_instellen.pdf
- TCP port of the inverter
    - Defaults to 8899
- The Wi-Fi device serial number
    - This can be found in the inverter's webinterface under Status -> Device information -> Device serial number
- The inverter serial number
    - This can be found in the inverter's webinterface under Status -> Connected Inverter -> Inverter serial number
- Polling interval (seconds)
    - Defaults to 60
