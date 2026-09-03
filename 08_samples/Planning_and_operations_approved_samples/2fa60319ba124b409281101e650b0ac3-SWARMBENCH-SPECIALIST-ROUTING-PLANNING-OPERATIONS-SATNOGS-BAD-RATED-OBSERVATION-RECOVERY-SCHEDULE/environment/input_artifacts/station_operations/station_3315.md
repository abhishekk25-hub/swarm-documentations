# Station 3315 - PARSEC 2

- Ground station ID: 3315
- Location: 51.4962, 11.9706 at 110 m AMSL
- Network page: https://network.satnogs.org/stations/3315/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into a PlutoSDR behind an inline SAW filter, driven from an Odroid in the loft. The shelter was rebuilt in June to keep damp out and the logs have been quiet ever since.

## Recent operating history

This site mostly serves the western horizon so our numbers should look familiar.

An unplanned outage from 2026-06-05T19:00:00Z to 2026-06-06T04:00:00Z took the site down when the rotator controller failed, and the site has been stable since and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Job intake is manual-review and the operator clears anything stuck by hand most evenings.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Availability for the recovery window

One thing for the recovery window: there is a hard blackout on this site from 11:00 on 25 July (UTC) to 19:00 on 25 July (UTC); the dish drive is being re-greased and re-aligned. Apologies for the inconvenience. To save you a wasted slot, we decline passes that do not clear 40 degrees at their highest point; the site sits in a bowl with high ground all round. We remain open either side of it. In short, we have room for 1 of these and no more; beyond that the upload queue backs up for days. We remain open either side of it.

## Antenna and rotator detail

The rotator is a SPID RAS driven over USB serial and pointing has held true since.

## Software and configuration

We track the upstream client but hold back one minor version so a rebuild takes under an hour.

## Neighbouring coverage

We coordinate informally with 4 nearby sites and the split has worked well so far.

## Typical traffic

The bulk of scheduled passes here are VHF with the rest spread across other bands.

## Staffing

Day-to-day operation is fully automated with the club providing cover during holidays.

## Power and connectivity

The site runs off a rooftop solar array with grid tie with two hours of battery behind it which has ridden out every cut so far this year. The site uses domestic fibre with a fixed address and transfers finish well inside the pass gap.

## Local interference

The local noise floor sits worst toward the east and it is documented in our station notes upstream.

## Calibration

We check frequency alignment monthly against a known beacon with results filed on the station page.

## Fault handling

Alerts route to the site owner first, then the club so problems rarely go unnoticed for long.

## Data quality

Frame decoding is handled downstream rather than on site and the effect is easy to spot on the waterfall. The receiver drifts by about 3 ppm between GPS corrections so treat marginal passes with a little caution.

## Other remarks

Our sister site 3345 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Station 3315 is reachable through the usual operator channels if anything here needs clarifying.
