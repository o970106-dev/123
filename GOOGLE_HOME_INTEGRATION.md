# Google Home Integration Setup Guide

## Overview
This property management system utilizes the **Double J CNS Broadcast** pattern for near-instant smart home control.

## Setup Steps

1. **GCP Project Configuration**:
   - Enable the Google Home Graph API.
   - Create a Service Account and download the JSON key.
   - Configure the Action on Google project with the fulfillment URL:
     `https://your-domain.wuchang.life/google_home/fulfillment`

2. **Odoo Module Installation**:
   - Install the `sc_google_home` module.
   - Generate a `google_home_token` for each user in their settings.

3. **Trait Support**:
   - **OnOff**: Standard light/switch control.
   - **Brightness**: 0-100% dimming.
   - **FanSpeed**: Multi-level fan control.
   - **Thermostat**: HVAC mode and temperature setting.

4. **O(1) Latency Optimization**:
   - The system uses SHA-256 absolute coordinates (STAPS) to map devices to edge nodes, ensuring sub-millisecond command execution.

## Troubleshooting
- Check the `collaboration_log.json` for signal transmission logs.
- Verify the STAPS multiplier is set to 8 for optimal parallel processing.
