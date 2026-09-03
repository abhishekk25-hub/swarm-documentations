# Station 37 - DL4PD

- Ground station ID: 37
- Location: 50.75, 6.216 at 277 m AMSL
- Network page: https://network.satnogs.org/stations/37/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into an Airspy R2 behind a bias-tee LNA at the mast head, driven from a rack-mounted NUC. Local noise improved once the EV charger was refiltered in February with no changes planned before the autumn.

## Recent operating history

Traffic through this site has been steady all summer and the pattern has been consistent.

An unplanned outage from 2026-06-14T21:00:00Z to 2026-06-15T06:00:00Z took the site down when the rotator controller failed, now fully resolved and with no bearing on the current recovery window.

## Scheduling and queue behaviour

The operator sweeps the queue once a day which keeps broken or duplicated requests off the air.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-15T19:00:00Z after the host was signed off, since when we have accepted work normally.

## Availability for the recovery window

One thing for the recovery window: we are able to run 1 catch-up observations at most; our SD cards are near end of life and we are rationing writes. Shout if that causes a problem.

## Antenna and rotator detail

The whole assembly was re-tensioned after the February storms which is adequate for the passes we take.

## Software and configuration

The host image was rebuilt in February onto the stock Raspbian image which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 4 neighbours to the west and duplicate scheduling is rare as a result.

## Typical traffic

Historically this site has specialised in S-band work and the hardware is tuned for that.

## Staffing

Two members handle maintenance between them though nobody is on site during the week.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 1 kW inverter and the generator has never actually been needed. Data leaves the site over a campus link and transfers finish well inside the pass gap.

## Local interference

A 368 MHz carrier appears most weekday afternoons which mostly affects the weaker downlinks.

## Calibration

Gain figures were re-measured after the February rebuild and drift since has been within tolerance.

## Fault handling

Anything unusual is logged and reviewed weekly though weekends can run to a day or two.

## Data quality

Baseline noise sits about 1 dB above the network median so raw audio is the better source if in doubt. Recordings are archived locally for 30 days and uploaded on completion though nothing has needed intervention this quarter.

## Other remarks

The 26 degree elevation floor this site used to run was lifted in March once the obstruction came down, so only the standard network minimum applies now.

## Contact

Contact details for station 37 are on its network page before you commit a booking.
