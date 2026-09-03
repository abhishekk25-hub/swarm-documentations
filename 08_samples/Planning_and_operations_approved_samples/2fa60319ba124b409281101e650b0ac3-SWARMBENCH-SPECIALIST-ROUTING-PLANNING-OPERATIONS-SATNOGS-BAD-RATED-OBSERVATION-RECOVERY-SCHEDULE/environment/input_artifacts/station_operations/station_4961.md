# Station 4961 - Berowra Groundstation

- Ground station ID: 4961
- Location: -33.62827, 151.143912 at 210 m AMSL
- Network page: https://network.satnogs.org/stations/4961/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into an Airspy Mini behind a switched attenuator for strong passes, driven from an old ThinkPad in the garage. This site replaced an older installation a few streets away which suits the unattended operating we do here.

## Recent operating history

We have been catching up on a backlog of our own since June which is worth knowing when you plan around us.

The Monday-morning routine maintenance we once ran between 0400Z and 1000Z ended in March and no longer applies.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs with a short grace period for cancellations.

The 18 degree elevation floor this site used to run was lifted in January once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

We are able to run 1 catch-up observations at most; the operator reviews each one by hand and cannot keep up beyond that. Other than that we are fully available. Every mode except GMSK is fine by us; sample rates for it exceed what the host can sustain. Please plan around it.

## Antenna and rotator detail

Azimuth travel is limited to 360 degrees by the mast stay and loss over that run is about 2.1 dB.

## Software and configuration

Automation here is a Docker deployment plus a handful of cron jobs so behaviour is predictable between updates.

## Neighbouring coverage

The nearest other station is roughly 310 km away which matters when we go offline.

## Typical traffic

Most of our traffic is UHF weather and cubesat work though we take whatever the network sends.

## Staffing

Two members handle maintenance between them with the club providing cover during holidays.

## Power and connectivity

A 2 kW supply feeds the shelter through an isolating transformer and the generator has never actually been needed. We backhaul over fixed wireless from the mast to the house so we compress artefacts before sending them.

## Local interference

The local noise floor sits worst toward the south-west and a notch filter has largely dealt with it.

## Calibration

Rotator alignment was re-surveyed in April and nothing has moved since.

## Fault handling

Escalation goes to whichever keyholder is on the rota and response is usually the same evening.

## Data quality

The receiver drifts by about 1 ppm between GPS corrections which rarely defeats the decoder outright. Low passes to the south pick up interference from a nearby telemetry link so the occasional pass gets clipped.

## Other remarks

A maintenance slot floated for 23 July at 05:30Z was cancelled when the replacement parts fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Station 4961 is reachable through the usual operator channels and we are happy to discuss alternatives.
