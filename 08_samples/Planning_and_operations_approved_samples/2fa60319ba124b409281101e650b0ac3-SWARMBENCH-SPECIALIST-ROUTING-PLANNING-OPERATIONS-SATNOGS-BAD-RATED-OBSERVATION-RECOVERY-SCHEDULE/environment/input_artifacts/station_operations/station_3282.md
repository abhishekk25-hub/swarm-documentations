# Station 3282 - ha7dcd and decent.org

- Ground station ID: 3282
- Location: 47.51747, 19.53215 at 175 m AMSL
- Network page: https://network.satnogs.org/stations/3282/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an SDRplay RSPdx behind a bias-tee LNA at the mast head, driven from an Odroid in the loft. Local noise improved once the solar inverter was refiltered in January and it has needed very little attention since.

## Recent operating history

Operating hours here are effectively unattended so expect the usual throughput.

Our sister site 3309 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Scheduling here is fully automated so late high-priority work lands in the next free slot.

An unplanned outage from 2026-06-12T06:00:00Z to 2026-06-12T15:00:00Z took the site down when the host machine failed, now fully resolved and with no bearing on the current recovery window.

## Availability for the recovery window

The Tuesday-morning routine maintenance we once ran between 0400Z and 1400Z ended in April and no longer applies. So you have it in writing: only passes reaching more than 35 degrees produce usable data; terrain noise dominates below that. Other than that we are fully available.

## Antenna and rotator detail

Azimuth travel is limited to 350 degrees by the mast stay which is adequate for the passes we take.

## Software and configuration

Scheduling is driven by the stock Raspbian image with local patches which has avoided the regressions others hit.

## Neighbouring coverage

We coordinate informally with 5 nearby sites which matters when we go offline.

## Typical traffic

Most of our traffic is UHF weather and cubesat work and results there are consistently good.

## Staffing

The station is run by 4 volunteers with the club providing cover during holidays.

## Power and connectivity

The rack draws about 65 W continuous from the club's metered feed and the generator has never actually been needed. The station has a dedicated ADSL line so we compress artefacts before sending them.

## Local interference

A survey in February found a persistent birdie near 297 MHz so we schedule around it where we can.

## Calibration

The chain was swept end to end in February and drift since has been within tolerance.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Baseline noise sits about 3 dB above the network median though nothing has needed intervention this quarter. Baseline noise sits about 3 dB above the network median so treat marginal passes with a little caution.

## Other remarks

The 18 degree elevation floor this site used to run was lifted in March once the obstruction came down, so only the standard network minimum applies now.

## Contact

Queries about station 3282 are best raised in the network chat if anything here needs clarifying.
