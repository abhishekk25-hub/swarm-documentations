# Station 2968 - UX5UL

- Ground station ID: 2968
- Location: 50.359, 30.388 at 200 m AMSL
- Network page: https://network.satnogs.org/stations/2968/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an Airspy Mini behind an inline SAW filter, driven from a Raspberry Pi 4. The shelter was rebuilt in February to keep damp out and it has needed very little attention since.

## Recent operating history

Volunteers rebuilt the feed arrangement in February which is worth knowing when you plan around us.

An unplanned outage from 2026-07-09T08:00:00Z to 2026-07-09T22:00:00Z took the site down when the network link failed, which is long behind us and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Scheduling here is fully automated with rejections reported straight back to the network.

Our sister site 2971 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

For the avoidance of doubt, our FSK chain is out of service, so do not book it; the filter for that path is out for repair. We remain open either side of it. Please note: we are dark for a service visit starting 20:45 UTC on the 23rd and finishing 04:45 UTC on the 24th; grounding work needs the whole chain isolated. That is the only limit from us.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over USB serial and pointing has held true since.

## Software and configuration

The host image was rebuilt in February onto a Docker deployment which has avoided the regressions others hit.

## Neighbouring coverage

This site sits inside a cluster of 2 stations which matters when we go offline.

## Typical traffic

Historically this site has specialised in S-band work so unusual modes occasionally surprise us.

## Staffing

Day-to-day operation is fully automated which keeps the workload manageable.

## Power and connectivity

Power comes from the building's landlord supply, backed by a 2 kW inverter and consumption has been stable since the rebuild. The station has a dedicated a campus link line so we compress artefacts before sending them.

## Local interference

Pager traffic near 212 MHz used to swamp us though it rarely reaches the passband we care about.

## Calibration

We check frequency alignment monthly against a known beacon so pointing errors should be under a degree.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Frame decoding is handled downstream rather than on site so raw audio is the better source if in doubt. Waterfall uploads occasionally stall on the domestic link so raw audio is the better source if in doubt.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-08T21:00:00Z after the rotator was signed off, since when we have accepted work normally.

## Contact

Queries about station 2968 are best raised in the network chat and we are happy to discuss alternatives.
