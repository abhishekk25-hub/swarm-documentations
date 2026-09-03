# Station 4255 - Goonhilly-M0XGH

- Ground station ID: 4255
- Location: 50.0482, -5.181 at 200 m AMSL
- Network page: https://network.satnogs.org/stations/4255/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a modified Wimo X-Quad into a HackRF One behind a switched attenuator for strong passes, driven from a Raspberry Pi 4. Local noise improved once the LED streetlight was refiltered in March though winter still costs us a handful of passes.

## Recent operating history

We have been catching up on a backlog of our own since March and nothing about that changes for the catch-up.

A maintenance slot floated for 23 July at 08:00Z was cancelled when the contractor fell through, pushing the work to August and leaving the station up throughout this window.

## Scheduling and queue behaviour

Our scheduler honours priority flags so late high-priority work lands in the next free slot.

Our sister site 4292 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

Station 4255 has nothing binding to declare for this window. Happy to take whatever you send.

## Antenna and rotator detail

The whole assembly was re-tensioned after the March storms which suits our mostly-overhead traffic.

## Software and configuration

The host image was rebuilt in March onto satnogs-client 1.9 and upgrades are applied only after the club tests them.

## Neighbouring coverage

There is no other coverage within about 269 km so a gap here is a genuine gap in coverage.

## Typical traffic

Historically this site has specialised in S-band work with the rest spread across other bands.

## Staffing

The site is unattended and checked remotely which keeps the workload manageable.

## Power and connectivity

We are on a domestic single-phase supply with no UPS on the receiver itself so brownouts show up as gaps rather than failures. We backhaul over a 4G modem from the mast to the house so large waterfall uploads queue up overnight.

## Local interference

The local noise floor sits worst toward the south-west though it rarely reaches the passband we care about.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source though we plan another check before winter.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

Frame decoding is handled downstream rather than on site and downstream products are unaffected. The receiver drifts by about 3 ppm between GPS corrections and downstream products are unaffected.

## Other remarks

A 7-booking weekly limit trialled during the June campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Station 4255 is reachable through the usual operator channels before you commit a booking.
