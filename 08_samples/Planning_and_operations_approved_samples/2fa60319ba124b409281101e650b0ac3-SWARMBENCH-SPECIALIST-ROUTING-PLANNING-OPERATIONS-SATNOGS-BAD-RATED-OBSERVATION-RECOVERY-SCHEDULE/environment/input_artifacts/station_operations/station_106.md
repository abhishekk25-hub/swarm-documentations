# Station 106 - BEEGND-1

- Ground station ID: 106
- Location: 52.073657, 12.462608 at 50 m AMSL
- Network page: https://network.satnogs.org/stations/106/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into a PlutoSDR behind a 20 dB mast-head amplifier, driven from an Odroid in the loft. Uptime last quarter ran at about 88 per cent and it has needed very little attention since.

## Recent operating history

Volunteers rebuilt the feed arrangement in May and nothing about that changes for the catch-up.

A maintenance slot floated for 25 July at 02:30Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 10 minutes and nothing already on air is ever pre-empted.

Our sister site 133 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

The main thing is that tower work is booked from 15:15Z on 22 July through 00:15Z on 24 July; grounding work needs the whole chain isolated. Everything else is unaffected. Before anything is booked, we decline passes that do not clear 38 degrees at their highest point; low-angle multipath here is severe. Apologies for the inconvenience. So you have it in writing: anything on FSK should go elsewhere; the relevant SDR channel is out for repair. Shout if that causes a problem. The 32 degree elevation floor this site used to run was lifted in January once the obstruction came down, so only the standard network minimum applies now.

## Antenna and rotator detail

We run LMR-600 between the shelter and the mast head which suits our mostly-overhead traffic.

## Software and configuration

We track the upstream client but hold back one minor version so a rebuild takes under an hour.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the north so handing work over is usually straightforward.

## Typical traffic

Historically this site has specialised in 2m and 70cm work which shapes how the antenna was built.

## Staffing

A rota of 4 keyholders shares the work and handover notes are kept on the club wiki.

## Power and connectivity

Everything here is fed from the club's metered feed via a residual-current breaker which has ridden out every cut so far this year. Uplink is ADSL shared with the household so we compress artefacts before sending them.

## Local interference

The local noise floor sits worst toward the east which the operator re-checks each quarter.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source though we plan another check before winter.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

The receiver drifts by about 2 ppm between GPS corrections and downstream products are unaffected. Baseline noise sits about 2 dB above the network median and the effect is easy to spot on the waterfall.

## Other remarks

The 32 degree elevation floor this site used to run was lifted in January once the obstruction came down, so only the standard network minimum applies now.

## Contact

Queries about station 106 are best raised in the network chat if anything here needs clarifying.
