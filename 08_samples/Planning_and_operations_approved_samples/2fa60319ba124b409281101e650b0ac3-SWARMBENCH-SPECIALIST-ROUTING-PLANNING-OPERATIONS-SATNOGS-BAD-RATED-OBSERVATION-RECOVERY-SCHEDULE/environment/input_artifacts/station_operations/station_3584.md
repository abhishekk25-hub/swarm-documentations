# Station 3584 - sat-rx

- Ground station ID: 3584
- Location: 51.904, -8.664 at 101 m AMSL
- Network page: https://network.satnogs.org/stations/3584/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into an SDRplay RSPdx behind a switched attenuator for strong passes, driven from a fanless mini-PC. Uptime last quarter ran at about 89 per cent which is about what we expect for this hardware.

## Recent operating history

We have been catching up on a backlog of our own since April and the pattern has been consistent.

The Wednesday-morning routine maintenance we once ran between 0800Z and 1200Z ended in March and no longer applies.

## Scheduling and queue behaviour

We cap pending work at roughly 40 jobs so a booked pass runs unless the site itself is unavailable.

A 6-booking weekly limit trialled during the January campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

An unplanned outage from 2026-07-09T20:00:00Z to 2026-07-10T02:00:00Z took the site down when the rotator controller failed, which is long behind us and with no bearing on the current recovery window. Station 3584 is open for the whole 22-25 July period. Normal scheduling rules apply.

## Antenna and rotator detail

We run LMR-400 between the shelter and the mast head which is adequate for the passes we take.

## Software and configuration

The host image was rebuilt in April onto satnogs-client 1.8 which has avoided the regressions others hit.

## Neighbouring coverage

There is no other coverage within about 225 km though we do not formally share a queue.

## Typical traffic

Most of our traffic is 2m and 70cm weather and cubesat work so unusual modes occasionally surprise us.

## Staffing

The site is unattended and checked remotely so response outside evenings can be slow.

## Power and connectivity

The rack draws about 78 W continuous from the club's metered feed though the changeover takes long enough to clip a recording. Data leaves the site over a 4G modem so we compress artefacts before sending them.

## Local interference

We see intermittent interference around 233 MHz from a neighbour which mostly affects the weaker downlinks.

## Calibration

The receiver was last calibrated against a GPSDO in April which keeps Doppler correction honest.

## Fault handling

Anything unusual is logged and reviewed weekly with a monthly summary to the network.

## Data quality

The receiver drifts by about 2 ppm between GPS corrections and the effect is easy to spot on the waterfall. Decoder success here has run around 89 per cent over the past year so raw audio is the better source if in doubt.

## Other remarks

A maintenance slot floated for 23 July at 05:00Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Station 3584 is reachable through the usual operator channels before you commit a booking.
