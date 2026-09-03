# Station 1561 - KK6NOW - Palm Desert, CA, US

- Ground station ID: 1561
- Location: 33.718908, -116.39262 at 100 m AMSL
- Network page: https://network.satnogs.org/stations/1561/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an Airspy R2 behind a cavity filter ahead of the receiver, driven from a Pi 5 with an SSD. The shelter was rebuilt in April to keep damp out and the owner checks it over most weekends.

## Recent operating history

This site mostly serves the western horizon and nothing about that changes for the catch-up.

The 18 degree elevation floor this site used to run was lifted in March once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

We cap pending work at roughly 30 jobs with rejections reported straight back to the network.

The Tuesday-morning routine maintenance we once ran between 0800Z and 1000Z ended in April and no longer applies.

## Availability for the recovery window

For the catch-up effort, nothing at all can be flown here before July 25; the rotator controller is with the vendor and there is no firm return date. Everything else is unaffected.

## Antenna and rotator detail

Azimuth travel is limited to 350 degrees by the mast stay and loss over that run is about 0.8 dB.

## Software and configuration

We deliberately run a Docker deployment rather than the rolling build so behaviour is predictable between updates.

## Neighbouring coverage

Our footprint overlaps 6 neighbours to the south and duplicate scheduling is rare as a result.

## Typical traffic

Most of our traffic is VHF weather and cubesat work and results there are consistently good.

## Staffing

The site is unattended and checked remotely which keeps the workload manageable.

## Power and connectivity

The site runs off a rooftop solar array with grid tie with two hours of battery behind it so a grid dip usually costs us a pass or two. Data leaves the site over fixed wireless so large waterfall uploads queue up overnight.

## Local interference

Pager traffic near 171 MHz used to swamp us so we schedule around it where we can.

## Calibration

We check frequency alignment monthly against a known beacon and nothing has moved since.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Frame decoding is handled downstream rather than on site which we are slowly working to improve. Frame decoding is handled downstream rather than on site which we are slowly working to improve.

## Other remarks

A tentative plan to embargo DUV work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Contact

Queries about station 1561 are best raised in the network chat and we usually reply within a day.
