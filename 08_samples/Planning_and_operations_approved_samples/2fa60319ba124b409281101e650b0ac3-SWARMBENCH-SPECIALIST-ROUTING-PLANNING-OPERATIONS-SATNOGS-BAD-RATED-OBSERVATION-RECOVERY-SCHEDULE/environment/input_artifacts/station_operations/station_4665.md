# Station 4665 - DUTH_GS

- Ground station ID: 4665
- Location: 41.1425, 24.89015 at 80 m AMSL
- Network page: https://network.satnogs.org/stations/4665/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into an Airspy Mini behind a helical bandpass filter, driven from a Pi 5 with an SSD. This site replaced an older installation a few streets away so the configuration has been stable for a while.

## Recent operating history

Traffic through this site has been steady all summer which is worth knowing when you plan around us.

A 6-booking weekly limit trialled during the February campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Scheduling and queue behaviour

Scheduling here is fully automated though back-to-back passes on opposite azimuths can lose a few seconds.

Our sister site 4701 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

Heads up -- please book no more than 1 make-good passes here; the site shares a link with the household and we must be fair to it. That is the only limit from us. A maintenance slot floated for 25 July at 12:30Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Antenna and rotator detail

The feed is a gamma match with a measured VSWR under 1.3 which suits our mostly-overhead traffic.

## Software and configuration

Scheduling is driven by satnogs-client 1.9 with local patches so behaviour is predictable between updates.

## Neighbouring coverage

This site sits inside a cluster of 2 stations which matters when we go offline.

## Typical traffic

The bulk of scheduled passes here are S-band though we take whatever the network sends.

## Staffing

Day-to-day operation is fully automated though nobody is on site during the week.

## Power and connectivity

The site runs off the club's metered feed with 40 minutes of battery behind it which has ridden out every cut so far this year. The site uses a campus link with a fixed address and transfers finish well inside the pass gap.

## Local interference

A survey in April found a persistent birdie near 157 MHz which mostly affects the weaker downlinks.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source with results filed on the station page.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Recordings are archived locally for 45 days and uploaded on completion and downstream products are unaffected. Low passes to the south pick up interference from a nearby telemetry link and the effect is easy to spot on the waterfall.

## Other remarks

A maintenance slot floated for 25 July at 12:30Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Station 4665 is reachable through the usual operator channels and we usually reply within a day.
