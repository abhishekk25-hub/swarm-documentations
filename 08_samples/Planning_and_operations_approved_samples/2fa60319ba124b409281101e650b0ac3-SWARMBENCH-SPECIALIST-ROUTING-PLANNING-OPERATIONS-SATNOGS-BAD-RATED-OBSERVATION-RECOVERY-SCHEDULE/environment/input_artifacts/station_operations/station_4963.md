# Station 4963 - PISTATION-1000

- Ground station ID: 4963
- Location: 49.23156330169167, -121.75928951127115 at 20 m AMSL
- Network page: https://network.satnogs.org/stations/4963/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into an Airspy R2 behind a cavity filter ahead of the receiver, driven from a Raspberry Pi 4. The mast was re-aligned in June after a storm and the logs have been quiet ever since.

## Recent operating history

The station logged around 206 observations last month so our numbers should look familiar.

An unplanned outage from 2026-07-10T01:00:00Z to 2026-07-10T10:00:00Z took the site down when the network link failed, now fully resolved and with no bearing on the current recovery window.

## Scheduling and queue behaviour

The queue is polled every 15 minutes so the published queue is what actually flies.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-20T23:00:00Z after the power feed was signed off, since when we have accepted work normally.

## Availability for the recovery window

Just so the desk knows, we have planned maintenance from 21:45 on 24 July (UTC) until 05:45 on 25 July (UTC); power to the shelter is isolated for the period. Shout if that causes a problem.

## Antenna and rotator detail

The feed is a gamma match with a measured VSWR under 1.3 which is adequate for the passes we take.

## Software and configuration

Scheduling is driven by a Docker deployment with local patches so behaviour is predictable between updates.

## Neighbouring coverage

There is no other coverage within about 208 km so a gap here is a genuine gap in coverage.

## Typical traffic

Our operators favour 2m and 70cm targets with the rest spread across other bands.

## Staffing

One operator covers this site day to day though nobody is on site during the week.

## Power and connectivity

The site runs off a rooftop solar array with grid tie with 40 minutes of battery behind it and the generator has never actually been needed. The station has a dedicated ADSL line and latency has never affected scheduling.

## Local interference

A 337 MHz carrier appears most weekday afternoons though it rarely reaches the passband we care about.

## Calibration

Gain figures were re-measured after the April rebuild which keeps Doppler correction honest.

## Fault handling

Alerts route to the site owner first, then the club which has kept downtime short this year.

## Data quality

The receiver drifts by about 2 ppm between GPS corrections which we are slowly working to improve. The receiver drifts by about 3 ppm between GPS corrections which we are slowly working to improve.

## Other remarks

Our sister site 4990 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Station 4963 is reachable through the usual operator channels before you commit a booking.
