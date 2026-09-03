# Station 1145 - VK4SMC #1

- Ground station ID: 1145
- Location: -16.448, 145.408 at 6 m AMSL
- Network page: https://network.satnogs.org/stations/1145/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an Airspy Mini behind a 20 dB mast-head amplifier, driven from an old ThinkPad in the garage. The shelter was rebuilt in January to keep damp out so the configuration has been stable for a while.

## Recent operating history

We have been catching up on a backlog of our own since January and nothing about that changes for the catch-up.

The 22 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

Scheduling here is fully automated and duplicate submissions are dropped automatically.

A 5-booking weekly limit trialled during the May campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

For planning purposes, 1 additional passes is all the site will manage; the operator is travelling and can only check in occasionally. That is the only limit from us.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.3 so slew time between passes is around 49 seconds.

## Software and configuration

Automation here is a Docker deployment plus a handful of cron jobs so behaviour is predictable between updates.

## Neighbouring coverage

The nearest other station is roughly 123 km away which matters when we go offline.

## Typical traffic

Roughly 86 per cent of our passes are 2m and 70cm with the rest spread across other bands.

## Staffing

One operator covers this site day to day and escalation is documented on the network page.

## Power and connectivity

We are on a rooftop solar array with grid tie with no UPS on the receiver itself so brownouts show up as gaps rather than failures. Data leaves the site over ADSL and latency has never affected scheduling.

## Local interference

Pager traffic near 443 MHz used to swamp us which mostly affects the weaker downlinks.

## Calibration

Rotator alignment was re-surveyed in January and drift since has been within tolerance.

## Fault handling

Anything unusual is logged and reviewed weekly so problems rarely go unnoticed for long.

## Data quality

The receiver drifts by about 4 ppm between GPS corrections so treat marginal passes with a little caution. Decoder success here has run around 99 per cent over the past year which we are slowly working to improve.

## Other remarks

An unplanned outage from 2026-07-07T11:00:00Z to 2026-07-08T13:00:00Z took the site down when the host machine failed, closed out at the time and with no bearing on the current recovery window.

## Contact

Scheduling questions go to the owner through the station 1145 profile page before you commit a booking.
