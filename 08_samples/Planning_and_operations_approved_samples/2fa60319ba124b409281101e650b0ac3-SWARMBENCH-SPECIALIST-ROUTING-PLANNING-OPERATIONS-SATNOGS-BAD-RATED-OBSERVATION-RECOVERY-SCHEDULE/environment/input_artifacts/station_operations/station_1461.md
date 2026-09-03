# Station 1461 - VE2DSK-VHF-UHF

- Ground station ID: 1461
- Location: 45.651, -73.564 at 45 m AMSL
- Network page: https://network.satnogs.org/stations/1461/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into a NooElec SmarTee behind an inline SAW filter, driven from a rack-mounted NUC. The club maintains it on a two-person on-call rota and it has needed very little attention since.

## Recent operating history

The station logged around 588 observations last month and nothing about that changes for the catch-up.

An unplanned outage from 2026-06-27T01:00:00Z to 2026-06-27T21:00:00Z took the site down when the rotator controller failed, closed out at the time and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Our scheduler honours priority flags and the operator clears anything stuck by hand most evenings.

The 22 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

So you have it in writing: we are able to run 1 catch-up observations at most; beyond that the upload queue backs up for days. Shout if that causes a problem. One thing for the recovery window: the array will be offline between 11:15Z on 22 July and 19:15Z on 22 July; the receiver is physically disconnected while the work happens. Outside that the site is open as normal. Before anything is booked, we ask schedulers to respect a 30 degree minimum peak elevation; terrain noise dominates below that. Everything else is unaffected.

## Antenna and rotator detail

Azimuth travel is limited to 350 degrees by the mast stay though it wants re-checking each spring.

## Software and configuration

Automation here is satnogs-client 1.8 plus a handful of cron jobs which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 3 neighbours to the west though we do not formally share a queue.

## Typical traffic

Historically this site has specialised in UHF work which shapes how the antenna was built.

## Staffing

Two members handle maintenance between them so response outside evenings can be slow.

## Power and connectivity

The site runs off the club's metered feed with a day of battery behind it so brownouts show up as gaps rather than failures. Uplink is a 4G modem shared with the household which occasionally drops during heavy weather.

## Local interference

A survey in April found a persistent birdie near 145 MHz and it is documented in our station notes upstream.

## Calibration

Gain figures were re-measured after the March rebuild though we plan another check before winter.

## Fault handling

The station reports its own health to a dashboard though weekends can run to a day or two.

## Data quality

Frame decoding is handled downstream rather than on site so treat marginal passes with a little caution. Frame decoding is handled downstream rather than on site and the effect is easy to spot on the waterfall.

## Other remarks

A 7-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Queries about station 1461 are best raised in the network chat before you commit a booking.
