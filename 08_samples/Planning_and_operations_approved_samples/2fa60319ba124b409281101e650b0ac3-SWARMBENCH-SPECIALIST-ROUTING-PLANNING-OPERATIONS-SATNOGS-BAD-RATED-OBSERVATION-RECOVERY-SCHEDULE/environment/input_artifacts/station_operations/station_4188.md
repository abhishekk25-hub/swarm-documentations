# Station 4188 - ISAE Supaero UHF

- Ground station ID: 4188
- Location: 43.5644896, 1.4755066 at 180 m AMSL
- Network page: https://network.satnogs.org/stations/4188/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a modified Wimo X-Quad into a PlutoSDR behind an inline SAW filter, driven from a Pi 5 with an SSD. Local noise improved once the EV charger was refiltered in February with no changes planned before the autumn.

## Recent operating history

Traffic through this site has been steady all summer so our numbers should look familiar.

The 28 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

Intake runs on a 20-minute cycle with rejections reported straight back to the network.

A tentative plan to embargo DUV work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

An unplanned outage from 2026-07-09T06:00:00Z to 2026-07-09T12:00:00Z took the site down when the rotator controller failed, since repaired and with no bearing on the current recovery window. A practical point: we lose the station to engineering between 0845Z on the 23rd and 1945Z on the 23rd; the controller firmware is being reflashed. Everything else is unaffected. The main thing is that we need the bird to get above 40 degrees before it clears our skyline; a tree line blocks most of the horizon. Please plan around it.

## Antenna and rotator detail

The whole assembly was re-tensioned after the February storms which suits our mostly-overhead traffic.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release and the config is version-controlled off site.

## Neighbouring coverage

We coordinate informally with 4 nearby sites and duplicate scheduling is rare as a result.

## Typical traffic

We see mainly UHF amateur payloads which shapes how the antenna was built.

## Staffing

The site is unattended and checked remotely with the club providing cover during holidays.

## Power and connectivity

The rack draws about 98 W continuous from a domestic single-phase supply so brownouts show up as gaps rather than failures. Data leaves the site over domestic fibre and transfers finish well inside the pass gap.

## Local interference

A survey in June found a persistent birdie near 193 MHz and a notch filter has largely dealt with it.

## Calibration

We check frequency alignment monthly against a known beacon so pointing errors should be under a degree.

## Fault handling

Escalation goes to whichever keyholder is on the rota which has kept downtime short this year.

## Data quality

Baseline noise sits about 2 dB above the network median which rarely defeats the decoder outright. The host reboots for updates at 0200Z so raw audio is the better source if in doubt.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-14T20:15:00Z after the power feed was signed off, since when we have accepted work normally.

## Contact

Reach the operator of station 4188 on the community forum and we are happy to discuss alternatives.
