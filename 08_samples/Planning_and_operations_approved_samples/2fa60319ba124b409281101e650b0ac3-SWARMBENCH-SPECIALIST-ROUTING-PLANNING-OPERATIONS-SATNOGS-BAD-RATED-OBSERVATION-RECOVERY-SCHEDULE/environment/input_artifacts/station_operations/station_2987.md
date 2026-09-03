# Station 2987 - VU2JEK_Nitin

- Ground station ID: 2987
- Location: 13.1458, 77.5417 at 900 m AMSL
- Network page: https://network.satnogs.org/stations/2987/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into an Airspy R2 behind a cavity filter ahead of the receiver, driven from a fanless mini-PC. The club maintains it on a two-person on-call rota and the logs have been quiet ever since.

## Recent operating history

This site mostly serves the southern horizon and nothing about that changes for the catch-up.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T05:00:00Z after the power feed was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

Intake runs on a 10-minute cycle so a booked pass runs unless the site itself is unavailable.

The Thursday-morning routine maintenance we once ran between 0500Z and 1100Z ended in March and no longer applies.

## Availability for the recovery window

For planning purposes, maintenance is locked in from 20:00 UTC on the 24th until 04:00 UTC on the 25th; the receiver is physically disconnected while the work happens. No other limits apply here. To save you a wasted slot, we can commit to a limit of 3 extra passes; beyond that the upload queue backs up for days. We remain open either side of it.

## Antenna and rotator detail

We run LMR-400 between the shelter and the mast head though it wants re-checking each spring.

## Software and configuration

Scheduling is driven by a Docker deployment with local patches though it does mean new features arrive late here.

## Neighbouring coverage

Our footprint overlaps 5 neighbours to the south though we do not formally share a queue.

## Typical traffic

Our operators favour UHF targets so unusual modes occasionally surprise us.

## Staffing

Day-to-day operation is fully automated so response outside evenings can be slow.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 5 kW inverter and consumption has been stable since the rebuild. Connectivity is domestic fibre, which is the weak point here and latency has never affected scheduling.

## Local interference

Pager traffic near 206 MHz used to swamp us so we schedule around it where we can.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source and nothing has moved since.

## Fault handling

Anything unusual is logged and reviewed weekly though weekends can run to a day or two.

## Data quality

Baseline noise sits about 4 dB above the network median which rarely defeats the decoder outright. Waterfall uploads occasionally stall on the domestic link though nothing has needed intervention this quarter.

## Other remarks

A 7-booking weekly limit trialled during the January campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Reach the operator of station 2987 on the community forum before you commit a booking.
