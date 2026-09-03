# Station 3258 - NuSpace SN1

- Ground station ID: 3258
- Location: 1.299, 103.771 at 49 m AMSL
- Network page: https://network.satnogs.org/stations/3258/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into a PlutoSDR behind a filtered preamp, driven from a Pi 5 with an SSD. Uptime last quarter ran at about 99 per cent and the logs have been quiet ever since.

## Recent operating history

Volunteers rebuilt the feed arrangement in March and the pattern has been consistent.

Our sister site 3282 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Scheduling here is fully automated and duplicate submissions are dropped automatically.

A maintenance slot floated for 25 July at 07:30Z was cancelled when the spare preamp fell through, pushing the work to August and leaving the station up throughout this window.

## Availability for the recovery window

A tentative plan to embargo DUV work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile. In short, nothing at all can be flown here before July 25; the site insurance lapsed and has to be renewed first. Normal service continues alongside.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over GPIO from the host which is adequate for the passes we take.

## Software and configuration

Scheduling is driven by a Docker deployment with local patches which has avoided the regressions others hit.

## Neighbouring coverage

There is no other coverage within about 284 km which matters when we go offline.

## Typical traffic

Most of our traffic is UHF weather and cubesat work and results there are consistently good.

## Staffing

The station is run by 2 volunteers so response outside evenings can be slow.

## Power and connectivity

We are on the club's metered feed with no UPS on the receiver itself and the generator has never actually been needed. Connectivity is fixed wireless, which is the weak point here so we compress artefacts before sending them.

## Local interference

The local noise floor sits worst toward the south-west so we schedule around it where we can.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source though we plan another check before winter.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

Frame decoding is handled downstream rather than on site so the occasional pass gets clipped. Baseline noise sits about 3 dB above the network median so the occasional pass gets clipped.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T05:00:00Z after the rotator was signed off, since when we have accepted work normally.

## Contact

Contact details for station 3258 are on its network page if anything here needs clarifying.
