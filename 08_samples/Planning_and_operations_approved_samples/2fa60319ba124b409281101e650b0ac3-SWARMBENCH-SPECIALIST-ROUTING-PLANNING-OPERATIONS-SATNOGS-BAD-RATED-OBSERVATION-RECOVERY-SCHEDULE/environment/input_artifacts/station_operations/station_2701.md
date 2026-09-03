# Station 2701 - DL2SKY

- Ground station ID: 2701
- Location: 48.871, 12.362 at 345 m AMSL
- Network page: https://network.satnogs.org/stations/2701/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a fixed zenith turnstile into an SDRplay RSPdx behind an inline SAW filter, driven from a Pi 5 with an SSD. Local noise improved once the LED streetlight was refiltered in May with no changes planned before the autumn.

## Recent operating history

The station logged around 417 observations last month though we do review anything anomalous.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-16T10:30:00Z after the preamp was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

Job intake is manual-review and released slots normally reappear within the hour.

An unplanned outage from 2026-06-06T15:00:00Z to 2026-06-07T05:00:00Z took the site down when the mains supply failed, which is long behind us and with no bearing on the current recovery window.

## Availability for the recovery window

A practical point: no FSK AX.100 Mode 5 please, though anything else is welcome; we have no working decoder for it at present. We remain open either side of it. A practical point: between 2026-07-24T22:30:00Z and 2026-07-25T20:30:00Z the antenna is committed to other work; the receiver is physically disconnected while the work happens. Shout if that causes a problem.

## Antenna and rotator detail

The feed is a gamma match with a measured VSWR under 1.3 so slew time between passes is around 21 seconds.

## Software and configuration

The host image was rebuilt in May onto satnogs-client 1.8 so a rebuild takes under an hour.

## Neighbouring coverage

We coordinate informally with 2 nearby sites so a gap here is a genuine gap in coverage.

## Typical traffic

Historically this site has specialised in 2m and 70cm work though we take whatever the network sends.

## Staffing

The site is unattended and checked remotely and handover notes are kept on the club wiki.

## Power and connectivity

A 1 kW supply feeds the shelter through an isolating transformer so a grid dip usually costs us a pass or two. Connectivity is domestic fibre, which is the weak point here which occasionally drops during heavy weather.

## Local interference

We see intermittent interference around 148 MHz from a neighbour which mostly affects the weaker downlinks.

## Calibration

Rotator alignment was re-surveyed in June which keeps Doppler correction honest.

## Fault handling

The operator is paged automatically on three consecutive failures and the log is public on request.

## Data quality

Waterfall uploads occasionally stall on the domestic link which we are slowly working to improve. The receiver drifts by about 3 ppm between GPS corrections though nothing has needed intervention this quarter.

## Other remarks

A maintenance slot floated for 23 July at 09:30Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Scheduling questions go to the owner through the station 2701 profile page and we are happy to discuss alternatives.
