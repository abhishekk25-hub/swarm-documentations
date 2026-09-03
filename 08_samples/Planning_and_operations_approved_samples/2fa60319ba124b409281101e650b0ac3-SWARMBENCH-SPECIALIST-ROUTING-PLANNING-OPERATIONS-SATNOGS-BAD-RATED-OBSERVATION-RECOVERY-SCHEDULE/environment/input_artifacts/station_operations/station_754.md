# Station 754 - W6MSU UHF

- Ground station ID: 754
- Location: 38.054, -121.361 at 10 m AMSL
- Network page: https://network.satnogs.org/stations/754/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into an RTL-SDR v4 behind an inline SAW filter, driven from a Raspberry Pi 4. Local noise improved once the EV charger was refiltered in June with no changes planned before the autumn.

## Recent operating history

The station logged around 621 observations last month though we do review anything anomalous.

Our sister site 786 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

The station accepts bookings up to 5 days ahead and anything unusual is reviewed before it runs.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

To save you a wasted slot, the site is only worth using above 35 degrees peak; our horizon is poor in almost every direction. We remain open either side of it.

## Antenna and rotator detail

The rotator is a SPID RAS driven over an Ethernet bridge though it wants re-checking each spring.

## Software and configuration

We deliberately run a Docker deployment rather than the rolling build and upgrades are applied only after the club tests them.

## Neighbouring coverage

There is no other coverage within about 114 km and duplicate scheduling is rare as a result.

## Typical traffic

The bulk of scheduled passes here are VHF so unusual modes occasionally surprise us.

## Staffing

Two members handle maintenance between them so response outside evenings can be slow.

## Power and connectivity

Power comes from the building's landlord supply, backed by a 5 kW inverter and the generator has never actually been needed. Uplink is fixed wireless shared with the household so we compress artefacts before sending them.

## Local interference

We see intermittent interference around 264 MHz from a neighbour which mostly affects the weaker downlinks.

## Calibration

We check frequency alignment monthly against a known beacon so pointing errors should be under a degree.

## Fault handling

The station reports its own health to a dashboard with a monthly summary to the network.

## Data quality

The receiver drifts by about 3 ppm between GPS corrections and downstream products are unaffected. Frame decoding is handled downstream rather than on site so raw audio is the better source if in doubt.

## Other remarks

The Tuesday-morning routine maintenance we once ran between 0700Z and 1300Z ended in June and no longer applies.

## Contact

Scheduling questions go to the owner through the station 754 profile page and we usually reply within a day.
