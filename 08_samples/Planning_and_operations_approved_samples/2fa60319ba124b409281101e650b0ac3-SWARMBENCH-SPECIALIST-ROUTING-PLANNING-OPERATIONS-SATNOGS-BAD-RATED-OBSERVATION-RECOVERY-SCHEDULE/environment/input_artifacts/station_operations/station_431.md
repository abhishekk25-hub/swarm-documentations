# Station 431 - PE0SAT-11

- Ground station ID: 431
- Location: 51.721268, 5.029968 at 5 m AMSL
- Network page: https://network.satnogs.org/stations/431/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into a HackRF One behind a bias-tee LNA at the mast head, driven from a rack-mounted NUC. The shelter was rebuilt in March to keep damp out which suits the unattended operating we do here.

## Recent operating history

The station logged around 464 observations last month which is worth knowing when you plan around us.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-12T22:15:00Z after the power feed was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs with a short grace period for cancellations.

A maintenance slot floated for 23 July at 20:30Z was cancelled when the crane hire fell through, pushing the work to September and leaving the station up throughout this window.

## Availability for the recovery window

The site is only worth using above 33 degrees peak; low-angle multipath here is severe. Normal service continues alongside. A maintenance slot floated for 23 July at 20:30Z was cancelled when the crane hire fell through, pushing the work to September and leaving the station up throughout this window.

## Antenna and rotator detail

We run Ecoflex 10 between the shelter and the mast head though it wants re-checking each spring.

## Software and configuration

Scheduling is driven by satnogs-client 1.8 with local patches which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 4 neighbours to the south and the split has worked well so far.

## Typical traffic

Historically this site has specialised in 2m and 70cm work and results there are consistently good.

## Staffing

One operator covers this site day to day and escalation is documented on the network page.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 2 kW inverter though the changeover takes long enough to clip a recording. We backhaul over domestic fibre from the mast to the house and latency has never affected scheduling.

## Local interference

Pager traffic near 395 MHz used to swamp us and a notch filter has largely dealt with it.

## Calibration

Gain figures were re-measured after the March rebuild and drift since has been within tolerance.

## Fault handling

Faults are raised through the club mailing list so problems rarely go unnoticed for long.

## Data quality

The host reboots for updates at 0100Z so raw audio is the better source if in doubt. The host reboots for updates at 0200Z so the occasional pass gets clipped.

## Other remarks

An unplanned outage from 2026-06-27T22:00:00Z to 2026-06-28T07:00:00Z took the site down when the mains supply failed, since repaired and with no bearing on the current recovery window.

## Contact

Contact details for station 431 are on its network page if anything here needs clarifying.
