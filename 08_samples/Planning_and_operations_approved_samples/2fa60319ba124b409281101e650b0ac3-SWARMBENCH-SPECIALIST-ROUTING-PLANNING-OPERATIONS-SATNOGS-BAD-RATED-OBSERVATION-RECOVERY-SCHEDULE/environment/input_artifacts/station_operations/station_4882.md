# Station 4882 - Shadi

- Ground station ID: 4882
- Location: 38.0170436840529, 23.732455911409634 at 210 m AMSL
- Network page: https://network.satnogs.org/stations/4882/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an Airspy Mini behind a filtered preamp, driven from a Pi 5 with an SSD. Uptime last quarter ran at about 92 per cent though winter still costs us a handful of passes.

## Recent operating history

This site mostly serves the eastern horizon and nothing about that changes for the catch-up.

Our sister site 4890 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

The operator sweeps the queue once a day though the overnight window is checked only once.

A maintenance slot floated for 24 July at 05:00Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Availability for the recovery window

For the catch-up effort, the station will not be answering the scheduler at all this week; the operator is away and nobody can cover the site. Do factor that into the plan.

## Antenna and rotator detail

The rotator is a SPID RAS driven over an Ethernet bridge which is adequate for the passes we take.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release and upgrades are applied only after the club tests them.

## Neighbouring coverage

There is no other coverage within about 66 km and duplicate scheduling is rare as a result.

## Typical traffic

Most of our traffic is UHF weather and cubesat work which shapes how the antenna was built.

## Staffing

The site is unattended and checked remotely so response outside evenings can be slow.

## Power and connectivity

A 3 kW supply feeds the shelter through an isolating transformer and consumption has been stable since the rebuild. Connectivity is ADSL, which is the weak point here and transfers finish well inside the pass gap.

## Local interference

A 141 MHz carrier appears most weekday afternoons though it rarely reaches the passband we care about.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source which keeps Doppler correction honest.

## Fault handling

The station reports its own health to a dashboard with a monthly summary to the network.

## Data quality

Frame decoding is handled downstream rather than on site so treat marginal passes with a little caution. Baseline noise sits about 3 dB above the network median so the occasional pass gets clipped.

## Other remarks

A 7-booking weekly limit trialled during the March campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Station 4882 is reachable through the usual operator channels and we are happy to discuss alternatives.
