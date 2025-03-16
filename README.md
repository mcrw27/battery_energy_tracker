# Battery Energy Tracker

A Home Assistant integration that tracks battery energy data, handling counter rollovers and providing accurate charge/discharge metrics.

## Features

- Accurate tracking of battery charge and discharge energy
- Handling of counter rollovers
- Estimation of charge time
- Diagnostic information
- Custom services for managing battery data

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Enter the URL of this repository and select "Integration" as the category
6. Click "Add"
7. Find "Battery Energy Tracker" in the list of integrations and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Unpack and copy the `custom_components/battery_energy_tracker` directory to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

Add to your `configuration.yaml`:

```yaml
battery_energy_tracker:
  battery_count: 4  # Number of batteries
  charge_rate: 1500  # Battery charging rate in Watts