# Station 579 - Um Alaish 4

- Ground station ID: 579
- Location: 29.1042, 48.125 at 20 m AMSL
- Network page: https://network.satnogs.org/stations/579/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into a NooElec SmarTee behind a filtered preamp, driven from a Raspberry Pi 4. The mast was re-aligned in April after a storm and it has needed very little attention since.

## Recent operating history

We have been catching up on a backlog of our own since April and nothing about that changes for the catch-up.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-11T07:15:00Z after the preamp was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

Intake runs on a 15-minute cycle and the operator clears anything stuck by hand most evenings.

The 22 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

Heads up -- maintenance is locked in from 0130Z on the 25th until 1230Z on the 25th; the dish drive is being re-greased and re-aligned. Other than that we are fully available. For this shift only, we can commit to a limit of 1 extra passes; our SD cards are near end of life and we are rationing writes. Normal service continues alongside. Our sister site 580 is offline this week for a rebuild, which is a different ground station and has no effect on availability here. For the avoidance of doubt, nothing shallower than 40 degrees is going to decode from this site; the neighbouring industrial estate wipes out the downlink at low angles. We will flag it if anything shifts.

## Antenna and rotator detail

The rotator is a ARSWIN controller driven over USB serial which suits our mostly-overhead traffic.

## Software and configuration

The host image was rebuilt in April onto satnogs-client 1.8 and upgrades are applied only after the club tests them.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the south so a gap here is a genuine gap in coverage.

## Typical traffic

We see mainly S-band amateur payloads and results there are consistently good.

## Staffing

Day-to-day operation is fully automated which keeps the workload manageable.

## Power and connectivity

We are on the club's metered feed with no UPS on the receiver itself and the generator has never actually been needed. Data leaves the site over a campus link though the monthly allowance is not generous.

## Local interference

A 445 MHz carrier appears most weekday afternoons which mostly affects the weaker downlinks.

## Calibration

We check frequency alignment monthly against a known beacon so pointing errors should be under a degree.

## Fault handling

Faults are raised through the club mailing list and the log is public on request.

## Data quality

The host reboots for updates at 0100Z so raw audio is the better source if in doubt. Decoder success here has run around 93 per cent over the past year and the effect is easy to spot on the waterfall.

## Other remarks

Our sister site 580 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Queries about station 579 are best raised in the network chat though replies can be slow at weekends.
