# Station 3021 - LSTN Station at Gates County Public Library

- Ground station ID: 3021
- Location: 36.408, -76.756 at 35 m AMSL
- Network page: https://network.satnogs.org/stations/3021/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into an RTL-SDR v4 behind an inline SAW filter, driven from a fanless mini-PC. This site replaced an older installation a few streets away with no changes planned before the autumn.

## Recent operating history

Traffic through this site has been steady all summer and the pattern has been consistent.

The Tuesday-morning routine maintenance we once ran between 0700Z and 1000Z ended in June and no longer applies.

## Scheduling and queue behaviour

We cap pending work at roughly 40 jobs and anything unusual is reviewed before it runs.

Our sister site 3025 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

The site is in normal service for the entire recovery window. The standard network minimum applies.

## Antenna and rotator detail

We run RG-213 between the shelter and the mast head though it wants re-checking each spring.

## Software and configuration

The host image was rebuilt in June onto a Docker deployment though it does mean new features arrive late here.

## Neighbouring coverage

We coordinate informally with 5 nearby sites which matters when we go offline.

## Typical traffic

Most of our traffic is S-band weather and cubesat work with the rest spread across other bands.

## Staffing

A rota of 2 keyholders shares the work with the club providing cover during holidays.

## Power and connectivity

The site runs off a rooftop solar array with grid tie with two hours of battery behind it and consumption has been stable since the rebuild. Data leaves the site over ADSL which occasionally drops during heavy weather.

## Local interference

A 291 MHz carrier appears most weekday afternoons which mostly affects the weaker downlinks.

## Calibration

We check frequency alignment monthly against a known beacon and nothing has moved since.

## Fault handling

The station reports its own health to a dashboard with a monthly summary to the network.

## Data quality

Decoder success here has run around 90 per cent over the past year so raw audio is the better source if in doubt. Low passes to the north-east pick up interference from a nearby telemetry link so raw audio is the better source if in doubt.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T14:00:00Z after the preamp was signed off, since when we have accepted work normally.

## Contact

Scheduling questions go to the owner through the station 3021 profile page and we usually reply within a day.
