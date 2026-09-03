# Station 3951 - UT4UYF/M

- Ground station ID: 3951
- Location: 50.559, 29.915 at 150 m AMSL
- Network page: https://network.satnogs.org/stations/3951/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into an SDRplay RSPdx behind a cavity filter ahead of the receiver, driven from a fanless mini-PC. Uptime last quarter ran at about 95 per cent and the logs have been quiet ever since.

## Recent operating history

Traffic through this site has been steady all summer and nothing about that changes for the catch-up.

The 18 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

The station accepts bookings up to 3 days ahead with a short grace period for cancellations.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-20T20:15:00Z after the host was signed off, since when we have accepted work normally.

## Availability for the recovery window

To save you a wasted slot, we need the bird to get above 43 degrees before it clears our skyline; low-angle multipath here is severe. We can take anything else you send us. An earlier revision of this note listed a booking freeze, lifted at 2026-07-20T20:15:00Z after the host was signed off, since when we have accepted work normally.

## Antenna and rotator detail

The whole assembly was re-tensioned after the June storms though it wants re-checking each spring.

## Software and configuration

We deliberately run satnogs-client 1.9 rather than the rolling build and the config is version-controlled off site.

## Neighbouring coverage

This site sits inside a cluster of 5 stations so a gap here is a genuine gap in coverage.

## Typical traffic

Most of our traffic is 2m and 70cm weather and cubesat work with the rest spread across other bands.

## Staffing

One operator covers this site day to day which keeps the workload manageable.

## Power and connectivity

Everything here is fed from a rooftop solar array with grid tie via a residual-current breaker and the generator has never actually been needed. Connectivity is ADSL, which is the weak point here which occasionally drops during heavy weather.

## Local interference

Broadband hash from a nearby installation peaks around 349 MHz though it rarely reaches the passband we care about.

## Calibration

We check frequency alignment monthly against a known beacon and drift since has been within tolerance.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

The receiver drifts by about 2 ppm between GPS corrections which rarely defeats the decoder outright. Frame decoding is handled downstream rather than on site which rarely defeats the decoder outright.

## Other remarks

An unplanned outage from 2026-07-09T15:00:00Z to 2026-07-10T00:00:00Z took the site down when the rotator controller failed, and the site has been stable since and with no bearing on the current recovery window.

## Contact

Contact details for station 3951 are on its network page if anything here needs clarifying.
