# Station 2154 - PC4L

- Ground station ID: 2154
- Location: 51.4901, 3.8236 at 0 m AMSL
- Network page: https://network.satnogs.org/stations/2154/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into a HackRF One behind a 20 dB mast-head amplifier, driven from a fanless mini-PC. The mast was re-aligned in March after a storm with no changes planned before the autumn.

## Recent operating history

The station logged around 322 observations last month and nothing about that changes for the catch-up.

An unplanned outage from 2026-06-15T13:00:00Z to 2026-06-15T22:00:00Z took the site down when the mains supply failed, now fully resolved and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Our scheduler honours priority flags and the rotator pre-positions a little ahead of AOS.

Our sister site 2163 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

Please note: we can commit to a limit of 1 extra passes; we are on a metered connection this month. We remain open either side of it. The 26 degree elevation floor this site used to run was lifted in March once the obstruction came down, so only the standard network minimum applies now.

## Antenna and rotator detail

Azimuth travel is limited to 360 degrees by the mast stay which suits our mostly-overhead traffic.

## Software and configuration

The host image was rebuilt in March onto satnogs-client 1.9 so behaviour is predictable between updates.

## Neighbouring coverage

The nearest other station is roughly 187 km away so a gap here is a genuine gap in coverage.

## Typical traffic

We see mainly S-band amateur payloads which shapes how the antenna was built.

## Staffing

A rota of 5 keyholders shares the work with the club providing cover during holidays.

## Power and connectivity

We are on the club's metered feed with no UPS on the receiver itself though the changeover takes long enough to clip a recording. Connectivity is a campus link, which is the weak point here so we compress artefacts before sending them.

## Local interference

Pager traffic near 186 MHz used to swamp us and a notch filter has largely dealt with it.

## Calibration

The chain was swept end to end in April and drift since has been within tolerance.

## Fault handling

The operator is paged automatically on three consecutive failures so problems rarely go unnoticed for long.

## Data quality

Frame decoding is handled downstream rather than on site and downstream products are unaffected. Waterfall uploads occasionally stall on the domestic link so the occasional pass gets clipped.

## Other remarks

A maintenance slot floated for 24 July at 12:30Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Contact details for station 2154 are on its network page if anything here needs clarifying.
