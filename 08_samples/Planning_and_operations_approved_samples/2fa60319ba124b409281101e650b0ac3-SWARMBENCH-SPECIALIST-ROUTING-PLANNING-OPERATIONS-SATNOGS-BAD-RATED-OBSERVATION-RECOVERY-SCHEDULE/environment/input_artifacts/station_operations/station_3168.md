# Station 3168 - OH2UDS- HS-MarsOnEarthProject-4-Finland

- Ground station ID: 3168
- Location: 60.146, 24.708 at 25 m AMSL
- Network page: https://network.satnogs.org/stations/3168/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into a PlutoSDR behind a filtered preamp, driven from a Pi 5 with an SSD. Uptime last quarter ran at about 93 per cent and it has needed very little attention since.

## Recent operating history

Volunteers rebuilt the feed arrangement in June so our numbers should look familiar.

An unplanned outage from 2026-06-03T00:00:00Z to 2026-06-03T20:00:00Z took the site down when the host machine failed, since repaired and with no bearing on the current recovery window.

## Scheduling and queue behaviour

The queue is polled every 20 minutes and the rotator pre-positions a little ahead of AOS.

Our sister site 3206 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

The 22 degree elevation floor this site used to run was lifted in January once the obstruction came down, so only the standard network minimum applies now. Station 3168 has nothing binding to declare for this window. We have capacity to spare this week.

## Antenna and rotator detail

The rotator is a SPID RAS driven over GPIO from the host and loss over that run is about 1.6 dB.

## Software and configuration

We deliberately run satnogs-client 1.9 rather than the rolling build though it does mean new features arrive late here.

## Neighbouring coverage

We coordinate informally with 5 nearby sites and duplicate scheduling is rare as a result.

## Typical traffic

Our operators favour 2m and 70cm targets so unusual modes occasionally surprise us.

## Staffing

Two members handle maintenance between them and handover notes are kept on the club wiki.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 5 kW inverter and the generator has never actually been needed. Data leaves the site over a campus link though the monthly allowance is not generous.

## Local interference

We see intermittent interference around 370 MHz from a neighbour though it rarely reaches the passband we care about.

## Calibration

Gain figures were re-measured after the May rebuild so pointing errors should be under a degree.

## Fault handling

Faults are raised through the club mailing list though weekends can run to a day or two.

## Data quality

Decoder success here has run around 93 per cent over the past year which we are slowly working to improve. The receiver drifts by about 3 ppm between GPS corrections and downstream products are unaffected.

## Other remarks

A tentative plan to embargo DUV work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Contact

Queries about station 3168 are best raised in the network chat before you commit a booking.
