# Station 4739 - F4arda_1

- Ground station ID: 4739
- Location: 48.9849228, 17.3886056 at 180 m AMSL
- Network page: https://network.satnogs.org/stations/4739/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into an SDRplay RSPdx behind a bias-tee LNA at the mast head, driven from a fanless mini-PC. The mast was re-aligned in April after a storm and the owner checks it over most weekends.

## Recent operating history

We have been catching up on a backlog of our own since April so expect the usual throughput.

An unplanned outage from 2026-06-03T08:00:00Z to 2026-06-04T04:00:00Z took the site down when the host machine failed, and the site has been stable since and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Scheduling here is fully automated and the operator clears anything stuck by hand most evenings.

The Tuesday-morning routine maintenance we once ran between 0400Z and 1000Z ended in May and no longer applies.

## Availability for the recovery window

For the catch-up effort, FSK passes will be rejected by the scheduler here; it shares hardware with the beacon monitor, which is tied up. Please plan around it. Ahead of the 22-25 July window, nothing shallower than 43 degrees is going to decode from this site; terrain noise dominates below that. We will flag it if anything shifts. An earlier revision of this note listed a booking freeze, lifted at 2026-07-20T05:45:00Z after the preamp was signed off, since when we have accepted work normally. A practical point: we are dark for a service visit starting 1815Z on the 22nd and finishing 1615Z on the 23rd; the preamp is being swapped out. Other than that we are fully available.

## Antenna and rotator detail

The whole assembly was re-tensioned after the April storms so slew time between passes is around 40 seconds.

## Software and configuration

The site runs a Docker deployment pinned to a known-good release so a rebuild takes under an hour.

## Neighbouring coverage

The regional group meets monthly to divide the load and duplicate scheduling is rare as a result.

## Typical traffic

The bulk of scheduled passes here are 2m and 70cm so unusual modes occasionally surprise us.

## Staffing

One operator covers this site day to day which keeps the workload manageable.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 5 kW inverter though the changeover takes long enough to clip a recording. Data leaves the site over domestic fibre though the monthly allowance is not generous.

## Local interference

Pager traffic near 315 MHz used to swamp us which the operator re-checks each quarter.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source so pointing errors should be under a degree.

## Fault handling

Anything unusual is logged and reviewed weekly which has kept downtime short this year.

## Data quality

Baseline noise sits about 4 dB above the network median which rarely defeats the decoder outright. Low passes to the north-east pick up interference from a nearby telemetry link though nothing has needed intervention this quarter.

## Other remarks

A maintenance slot floated for 23 July at 15:00Z was cancelled when the crane hire fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Station 4739 is reachable through the usual operator channels if anything here needs clarifying.
