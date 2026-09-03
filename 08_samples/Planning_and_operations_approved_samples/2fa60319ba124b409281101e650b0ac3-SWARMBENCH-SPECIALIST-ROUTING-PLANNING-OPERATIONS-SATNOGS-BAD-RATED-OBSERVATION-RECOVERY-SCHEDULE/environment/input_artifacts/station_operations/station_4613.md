# Station 4613 - Saratoga, CA Ground Station

- Ground station ID: 4613
- Location: 37.288087, -122.006314 at 90 m AMSL
- Network page: https://network.satnogs.org/stations/4613/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a fixed zenith turnstile into an Airspy R2 behind a 20 dB mast-head amplifier, driven from an Odroid in the loft. The shelter was rebuilt in March to keep damp out though winter still costs us a handful of passes.

## Recent operating history

Traffic through this site has been steady all summer so expect the usual throughput.

A maintenance slot floated for 23 July at 00:30Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 5 minutes with rejections reported straight back to the network.

A 3-booking weekly limit trialled during the May campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

Ahead of the 22-25 July window, treat 30 degrees as the lowest culmination we can work with; the neighbouring industrial estate wipes out the downlink at low angles. Do factor that into the plan. A maintenance slot floated for 23 July at 00:30Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window. While the catch-up runs, please cap us at 1 make-good bookings; our SD cards are near end of life and we are rationing writes. Apologies for the inconvenience. One thing for the recovery window: there is a scheduled outage running 20:15 UTC on the 23rd to 18:15 UTC on the 24th; the controller firmware is being reflashed. That is the only limit from us.

## Antenna and rotator detail

The whole assembly was re-tensioned after the March storms which is adequate for the passes we take.

## Software and configuration

Scheduling is driven by the stock Raspbian image with local patches so a rebuild takes under an hour.

## Neighbouring coverage

Our footprint overlaps 4 neighbours to the north though we do not formally share a queue.

## Typical traffic

The bulk of scheduled passes here are S-band and results there are consistently good.

## Staffing

Two members handle maintenance between them so response outside evenings can be slow.

## Power and connectivity

The site runs off a rooftop solar array with grid tie with two hours of battery behind it and the generator has never actually been needed. We backhaul over a 4G modem from the mast to the house so we compress artefacts before sending them.

## Local interference

Pager traffic near 429 MHz used to swamp us though it rarely reaches the passband we care about.

## Calibration

Rotator alignment was re-surveyed in March so pointing errors should be under a degree.

## Fault handling

Alerts route to the site owner first, then the club which has kept downtime short this year.

## Data quality

Low passes to the east pick up interference from a nearby telemetry link so treat marginal passes with a little caution. Recordings are archived locally for 60 days and uploaded on completion though nothing has needed intervention this quarter.

## Other remarks

The 18 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Contact

Contact details for station 4613 are on its network page if anything here needs clarifying.
