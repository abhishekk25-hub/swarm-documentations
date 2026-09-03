# Station 3804 - DP0GVN-UHF

- Ground station ID: 3804
- Location: -70.658667, -8.284667 at 15 m AMSL
- Network page: https://network.satnogs.org/stations/3804/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into an Airspy Mini behind a filtered preamp, driven from a Raspberry Pi 4. The club maintains it on a two-person on-call rota so the configuration has been stable for a while.

## Recent operating history

Operating hours here are effectively unattended so expect the usual throughput.

An unplanned outage from 2026-06-17T06:00:00Z to 2026-06-18T08:00:00Z took the site down when the host machine failed, which is long behind us and with no bearing on the current recovery window.

## Scheduling and queue behaviour

The queue is polled every 15 minutes which keeps broken or duplicated requests off the air.

A maintenance slot floated for 24 July at 22:30Z was cancelled when the replacement parts fell through, pushing the work to September and leaving the station up throughout this window.

## Availability for the recovery window

No maintenance, no embargo and no cap at station 3804 this week. The standard network minimum applies.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.5 so slew time between passes is around 89 seconds.

## Software and configuration

We track the upstream client but hold back one minor version and upgrades are applied only after the club tests them.

## Neighbouring coverage

This site sits inside a cluster of 5 stations and duplicate scheduling is rare as a result.

## Typical traffic

Most of our traffic is UHF weather and cubesat work and results there are consistently good.

## Staffing

Day-to-day operation is fully automated which keeps the workload manageable.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 5 kW inverter though the changeover takes long enough to clip a recording. Uplink is a campus link shared with the household which occasionally drops during heavy weather.

## Local interference

A 248 MHz carrier appears most weekday afternoons though it rarely reaches the passband we care about.

## Calibration

We check frequency alignment monthly against a known beacon and drift since has been within tolerance.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Low passes to the north pick up interference from a nearby telemetry link so the occasional pass gets clipped. Frame decoding is handled downstream rather than on site so the occasional pass gets clipped.

## Other remarks

Our sister site 3841 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Station 3804 is reachable through the usual operator channels before you commit a booking.
