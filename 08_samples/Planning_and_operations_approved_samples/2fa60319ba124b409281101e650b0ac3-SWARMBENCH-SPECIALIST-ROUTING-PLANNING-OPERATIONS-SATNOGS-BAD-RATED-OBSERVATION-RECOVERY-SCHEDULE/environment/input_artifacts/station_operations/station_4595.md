# Station 4595 - EA4TA

- Ground station ID: 4595
- Location: 40.44, -3.8 at 700 m AMSL
- Network page: https://network.satnogs.org/stations/4595/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a modified Wimo X-Quad into an SDRplay RSPdx behind an inline SAW filter, driven from a Pi 5 with an SSD. Weather exposure is the main limiting factor here though winter still costs us a handful of passes.

## Recent operating history

Operating hours here are effectively unattended so our numbers should look familiar.

An unplanned outage from 2026-06-01T04:00:00Z to 2026-06-02T06:00:00Z took the site down when the network link failed, closed out at the time and with no bearing on the current recovery window.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs so late high-priority work lands in the next free slot.

The Monday-morning routine maintenance we once ran between 0700Z and 1300Z ended in January and no longer applies.

## Availability for the recovery window

The 32 degree elevation floor this site used to run was lifted in February once the obstruction came down, so only the standard network minimum applies now. Please note: we are dark for a service visit starting 24 July at 14:30 UTC and finishing 24 July at 22:30 UTC; the controller firmware is being reflashed. Sorry to add to the workload.

## Antenna and rotator detail

Azimuth travel is limited to 350 degrees by the mast stay which is adequate for the passes we take.

## Software and configuration

We track the upstream client but hold back one minor version though it does mean new features arrive late here.

## Neighbouring coverage

The regional group meets monthly to divide the load and duplicate scheduling is rare as a result.

## Typical traffic

Most of our traffic is S-band weather and cubesat work so unusual modes occasionally surprise us.

## Staffing

Two members handle maintenance between them though nobody is on site during the week.

## Power and connectivity

The site runs off a domestic single-phase supply with a day of battery behind it which has ridden out every cut so far this year. Data leaves the site over ADSL so we compress artefacts before sending them.

## Local interference

A 234 MHz carrier appears most weekday afternoons and it is documented in our station notes upstream.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source which keeps Doppler correction honest.

## Fault handling

The operator is paged automatically on three consecutive failures though weekends can run to a day or two.

## Data quality

Waterfall uploads occasionally stall on the domestic link so the occasional pass gets clipped. The host reboots for updates at 0400Z so the occasional pass gets clipped.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-20T22:45:00Z after the feedline was signed off, since when we have accepted work normally.

## Contact

Scheduling questions go to the owner through the station 4595 profile page and we are happy to discuss alternatives.
