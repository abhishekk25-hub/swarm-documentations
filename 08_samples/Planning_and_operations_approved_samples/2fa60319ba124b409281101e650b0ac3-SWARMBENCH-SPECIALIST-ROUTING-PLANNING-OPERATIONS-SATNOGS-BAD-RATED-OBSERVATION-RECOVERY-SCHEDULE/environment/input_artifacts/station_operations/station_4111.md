# Station 4111 - Plyachka

- Ground station ID: 4111
- Location: 42.48304, 23.445813 at 1100 m AMSL
- Network page: https://network.satnogs.org/stations/4111/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a fixed zenith turnstile into a PlutoSDR behind an inline SAW filter, driven from a rack-mounted NUC. Uptime last quarter ran at about 90 per cent and the owner checks it over most weekends.

## Recent operating history

This site mostly serves the northern horizon though we do review anything anomalous.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-13T16:15:00Z after the preamp was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

Job intake is manual-review and nothing already on air is ever pre-empted.

A 2-booking weekly limit trialled during the June campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

One thing for the recovery window: the site drops out for planned work from 2026-07-23T20:15:00Z to 2026-07-24T23:15:00Z; the receiver is physically disconnected while the work happens. Anything outside that scope is fine. Please note: 1 additional passes is all the site will manage; the site shares a link with the household and we must be fair to it. The rest of the window is clear.

## Antenna and rotator detail

The rotator is a SPID RAS driven over an Ethernet bridge and pointing has held true since.

## Software and configuration

We deliberately run the stock Raspbian image rather than the rolling build and upgrades are applied only after the club tests them.

## Neighbouring coverage

Our footprint overlaps 6 neighbours to the east so handing work over is usually straightforward.

## Typical traffic

Most of our traffic is S-band weather and cubesat work though we take whatever the network sends.

## Staffing

The station is run by 2 volunteers which keeps the workload manageable.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 1 kW inverter and consumption has been stable since the rebuild. The site uses fixed wireless with a fixed address though the monthly allowance is not generous.

## Local interference

The local noise floor sits worst toward the south-west though it rarely reaches the passband we care about.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source though we plan another check before winter.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

Baseline noise sits about 4 dB above the network median so the occasional pass gets clipped. The receiver drifts by about 2 ppm between GPS corrections and the effect is easy to spot on the waterfall.

## Other remarks

The 22 degree elevation floor this site used to run was lifted in June once the obstruction came down, so only the standard network minimum applies now.

## Contact

Scheduling questions go to the owner through the station 4111 profile page and we usually reply within a day.
