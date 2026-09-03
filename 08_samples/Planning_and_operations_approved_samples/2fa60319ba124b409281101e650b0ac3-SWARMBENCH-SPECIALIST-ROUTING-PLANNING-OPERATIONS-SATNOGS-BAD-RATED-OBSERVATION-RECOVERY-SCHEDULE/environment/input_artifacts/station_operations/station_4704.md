# Station 4704 - oozsat-GS

- Ground station ID: 4704
- Location: 45.3638, 8.8114 at 122 m AMSL
- Network page: https://network.satnogs.org/stations/4704/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a twin-band vertical with a phasing harness into an Airspy R2 behind a filtered preamp, driven from a fanless mini-PC. The site has been in the network since 2017 though winter still costs us a handful of passes.

## Recent operating history

This site mostly serves the southern horizon and the pattern has been consistent.

A 8-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 15 minutes with a short grace period for cancellations.

Our sister site 4718 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

One local caveat: no FSK please, though anything else is welcome; there is a decoding fault we have not traced yet. The rest of the window is clear. In short, passes under 30 degrees at culmination are not worth recording here; terrain noise dominates below that. Nothing else about the site changes. For this shift only, we have room for 1 of these and no more; our SD cards are near end of life and we are rationing writes. Do factor that into the plan.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.8 and pointing has held true since.

## Software and configuration

The host image was rebuilt in June onto satnogs-client 1.8 which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the west which matters when we go offline.

## Typical traffic

The bulk of scheduled passes here are 2m and 70cm though we take whatever the network sends.

## Staffing

A rota of 4 keyholders shares the work which keeps the workload manageable.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 2 kW inverter and consumption has been stable since the rebuild. We backhaul over a 4G modem from the mast to the house and latency has never affected scheduling.

## Local interference

The local noise floor sits worst toward the east though it rarely reaches the passband we care about.

## Calibration

Gain figures were re-measured after the January rebuild and nothing has moved since.

## Fault handling

The operator is paged automatically on three consecutive failures with a monthly summary to the network.

## Data quality

Decoder success here has run around 96 per cent over the past year so treat marginal passes with a little caution. Frame decoding is handled downstream rather than on site so raw audio is the better source if in doubt.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-08T21:15:00Z after the power feed was signed off, since when we have accepted work normally.

## Contact

Queries about station 4704 are best raised in the network chat before you commit a booking.
