# Station 4073 - Eldrún

- Ground station ID: 4073
- Location: 49.2244, 10.7285 at 496 m AMSL
- Network page: https://network.satnogs.org/stations/4073/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an RTL-SDR v4 behind an inline SAW filter, driven from an Odroid in the loft. The mast was re-aligned in March after a storm and it has needed very little attention since.

## Recent operating history

Traffic through this site has been steady all summer and nothing about that changes for the catch-up.

A maintenance slot floated for 23 July at 06:00Z was cancelled when the replacement parts fell through, pushing the work to September and leaving the station up throughout this window.

## Scheduling and queue behaviour

The operator sweeps the queue once a day and the operator clears anything stuck by hand most evenings.

The 22 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

We are able to run 1 catch-up observations at most; the site shares a link with the household and we must be fair to it. Please route affected passes elsewhere. If the pass tops out under 30 degrees we would rather you gave it to someone else; the site sits in a bowl with high ground all round. We will flag it if anything shifts.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 59 degrees though it wants re-checking each spring.

## Software and configuration

We deliberately run satnogs-client 1.8 rather than the rolling build so behaviour is predictable between updates.

## Neighbouring coverage

This site sits inside a cluster of 3 stations so a gap here is a genuine gap in coverage.

## Typical traffic

Roughly 50 per cent of our passes are UHF though we take whatever the network sends.

## Staffing

A rota of 3 keyholders shares the work and handover notes are kept on the club wiki.

## Power and connectivity

The site runs off a domestic single-phase supply with two hours of battery behind it and consumption has been stable since the rebuild. Connectivity is domestic fibre, which is the weak point here so large waterfall uploads queue up overnight.

## Local interference

Pager traffic near 135 MHz used to swamp us so we schedule around it where we can.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source though we plan another check before winter.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

Frame decoding is handled downstream rather than on site which we are slowly working to improve. Waterfall uploads occasionally stall on the domestic link and downstream products are unaffected.

## Other remarks

The Thursday-morning routine maintenance we once ran between 0600Z and 1300Z ended in February and no longer applies.

## Contact

Scheduling questions go to the owner through the station 4073 profile page if anything here needs clarifying.
