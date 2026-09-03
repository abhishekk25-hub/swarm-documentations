# Station 2138 - OM7AAK

- Ground station ID: 2138
- Location: 48.336, 17.448 at 134 m AMSL
- Network page: https://network.satnogs.org/stations/2138/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into an RTL-SDR v4 behind a switched attenuator for strong passes, driven from a Raspberry Pi 4. Local noise improved once the EV charger was refiltered in March which suits the unattended operating we do here.

## Recent operating history

Volunteers rebuilt the feed arrangement in March though we do review anything anomalous.

Our sister site 2143 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Intake runs on a 5-minute cycle and the rotator pre-positions a little ahead of AOS.

An unplanned outage from 2026-07-06T00:00:00Z to 2026-07-06T14:00:00Z took the site down when the host machine failed, now fully resolved and with no bearing on the current recovery window.

## Availability for the recovery window

Ahead of the 22-25 July window, we are declining FSK passes for now; the relevant SDR channel is out for repair. The rest of the window is clear.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.3 which is adequate for the passes we take.

## Software and configuration

The host image was rebuilt in March onto satnogs-client 1.9 and the config is version-controlled off site.

## Neighbouring coverage

The nearest other station is roughly 35 km away so a gap here is a genuine gap in coverage.

## Typical traffic

Roughly 88 per cent of our passes are UHF which shapes how the antenna was built.

## Staffing

Day-to-day operation is fully automated and escalation is documented on the network page.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 3 kW inverter and the generator has never actually been needed. The station has a dedicated a 4G modem line which occasionally drops during heavy weather.

## Local interference

A 164 MHz carrier appears most weekday afternoons though it rarely reaches the passband we care about.

## Calibration

Rotator alignment was re-surveyed in June though we plan another check before winter.

## Fault handling

The station reports its own health to a dashboard and response is usually the same evening.

## Data quality

Frame decoding is handled downstream rather than on site so the occasional pass gets clipped. The host reboots for updates at 0400Z which rarely defeats the decoder outright.

## Other remarks

A 3-booking weekly limit trialled during the March campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Station 2138 is reachable through the usual operator channels though replies can be slow at weekends.
