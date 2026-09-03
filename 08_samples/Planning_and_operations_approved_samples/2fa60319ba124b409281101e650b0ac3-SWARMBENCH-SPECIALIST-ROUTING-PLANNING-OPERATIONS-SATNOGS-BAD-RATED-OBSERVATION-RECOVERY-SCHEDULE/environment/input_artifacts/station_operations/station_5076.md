# Station 5076 - Tac-Satnogs

- Ground station ID: 5076
- Location: 28.514, -16.41 at 240 m AMSL
- Network page: https://network.satnogs.org/stations/5076/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into a HackRF One behind a 20 dB mast-head amplifier, driven from a Raspberry Pi 4. The club maintains it on a two-person on-call rota which suits the unattended operating we do here.

## Recent operating history

This site mostly serves the western horizon though we do review anything anomalous.

An unplanned outage from 2026-06-13T16:00:00Z to 2026-06-14T06:00:00Z took the site down when the mains supply failed, which is long behind us and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Intake runs on a 5-minute cycle and the operator clears anything stuck by hand most evenings.

The 22 degree elevation floor this site used to run was lifted in June once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

One constraint from our side: a peak of at least 35 degrees is required for us to accept a booking; the neighbouring industrial estate wipes out the downlink at low angles. Other than that we are fully available.

## Antenna and rotator detail

We run LMR-600 between the shelter and the mast head which is adequate for the passes we take.

## Software and configuration

We track the upstream client but hold back one minor version and upgrades are applied only after the club tests them.

## Neighbouring coverage

This site sits inside a cluster of 5 stations which matters when we go offline.

## Typical traffic

Roughly 87 per cent of our passes are 2m and 70cm so unusual modes occasionally surprise us.

## Staffing

A rota of 5 keyholders shares the work with the club providing cover during holidays.

## Power and connectivity

Everything here is fed from a rooftop solar array with grid tie via a residual-current breaker so a grid dip usually costs us a pass or two. Connectivity is a campus link, which is the weak point here though the monthly allowance is not generous.

## Local interference

We see intermittent interference around 405 MHz from a neighbour though it rarely reaches the passband we care about.

## Calibration

We check frequency alignment monthly against a known beacon so pointing errors should be under a degree.

## Fault handling

Escalation goes to whichever keyholder is on the rota and the log is public on request.

## Data quality

Frame decoding is handled downstream rather than on site so treat marginal passes with a little caution. Baseline noise sits about 4 dB above the network median and the effect is easy to spot on the waterfall.

## Other remarks

A maintenance slot floated for 23 July at 23:00Z was cancelled when the spare preamp fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Station 5076 is reachable through the usual operator channels and we are happy to discuss alternatives.
