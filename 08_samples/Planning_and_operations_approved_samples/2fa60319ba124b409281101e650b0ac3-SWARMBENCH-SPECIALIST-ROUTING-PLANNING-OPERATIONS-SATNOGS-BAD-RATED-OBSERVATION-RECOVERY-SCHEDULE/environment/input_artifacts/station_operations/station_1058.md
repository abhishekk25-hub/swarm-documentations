# Station 1058 - DEOS_RALF

- Ground station ID: 1058
- Location: 43.5649, 1.4751 at 145 m AMSL
- Network page: https://network.satnogs.org/stations/1058/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an Airspy R2 behind an inline SAW filter, driven from a fanless mini-PC. Uptime last quarter ran at about 99 per cent which suits the unattended operating we do here.

## Recent operating history

This site mostly serves the northern horizon which is worth knowing when you plan around us.

A maintenance slot floated for 23 July at 19:30Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Scheduling and queue behaviour

Intake runs on a 15-minute cycle though the overnight window is checked only once.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T12:45:00Z after the rotator was signed off, since when we have accepted work normally.

## Availability for the recovery window

Worth flagging before you schedule: if the pass tops out under 33 degrees we would rather you gave it to someone else; a tree line blocks most of the horizon. Normal service continues alongside. A practical point: maintenance is locked in from 2026-07-22T10:15:00Z until 2026-07-22T21:15:00Z; the controller firmware is being reflashed. Do factor that into the plan.

## Antenna and rotator detail

Azimuth travel is limited to 340 degrees by the mast stay which suits our mostly-overhead traffic.

## Software and configuration

The host image was rebuilt in May onto satnogs-client 1.9 which has avoided the regressions others hit.

## Neighbouring coverage

The regional group meets monthly to divide the load so handing work over is usually straightforward.

## Typical traffic

The bulk of scheduled passes here are UHF so unusual modes occasionally surprise us.

## Staffing

The station is run by 2 volunteers and handover notes are kept on the club wiki.

## Power and connectivity

A 3 kW supply feeds the shelter through an isolating transformer which has ridden out every cut so far this year. The site uses a 4G modem with a fixed address which occasionally drops during heavy weather.

## Local interference

A 327 MHz carrier appears most weekday afternoons so we schedule around it where we can.

## Calibration

The receiver was last calibrated against a GPSDO in January and nothing has moved since.

## Fault handling

The station reports its own health to a dashboard though weekends can run to a day or two.

## Data quality

Baseline noise sits about 1 dB above the network median which we are slowly working to improve. Low passes to the east pick up interference from a nearby telemetry link so the occasional pass gets clipped.

## Other remarks

The Monday-morning routine maintenance we once ran between 0400Z and 1100Z ended in April and no longer applies.

## Contact

Reach the operator of station 1058 on the community forum if anything here needs clarifying.
