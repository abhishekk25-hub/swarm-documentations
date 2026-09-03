# Station 766 - Dunchurch

- Ground station ID: 766
- Location: 52.342463, -1.290348 at 128 m AMSL
- Network page: https://network.satnogs.org/stations/766/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into an RTL-SDR v4 behind a 20 dB mast-head amplifier, driven from an Odroid in the loft. This site replaced an older installation a few streets away and it has needed very little attention since.

## Recent operating history

The station logged around 267 observations last month though we do review anything anomalous.

Our sister site 797 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 10 minutes and the operator clears anything stuck by hand most evenings.

A 6-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

One thing for the recovery window: this site can absorb at most 3 additional catch-up observations; the operator is travelling and can only check in occasionally. Please route affected passes elsewhere.

## Antenna and rotator detail

The rotator is a ARSWIN controller driven over GPIO from the host and pointing has held true since.

## Software and configuration

We track the upstream client but hold back one minor version and the config is version-controlled off site.

## Neighbouring coverage

This site sits inside a cluster of 6 stations so handing work over is usually straightforward.

## Typical traffic

Historically this site has specialised in VHF work with the rest spread across other bands.

## Staffing

A rota of 2 keyholders shares the work and handover notes are kept on the club wiki.

## Power and connectivity

Everything here is fed from the club's metered feed via a residual-current breaker and the generator has never actually been needed. Data leaves the site over fixed wireless and transfers finish well inside the pass gap.

## Local interference

A 374 MHz carrier appears most weekday afternoons which the operator re-checks each quarter.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source and nothing has moved since.

## Fault handling

Faults are raised through the club mailing list and response is usually the same evening.

## Data quality

Frame decoding is handled downstream rather than on site and the effect is easy to spot on the waterfall. Decoder success here has run around 98 per cent over the past year so the occasional pass gets clipped.

## Other remarks

An unplanned outage from 2026-06-01T07:00:00Z to 2026-06-01T13:00:00Z took the site down when the rotator controller failed, closed out at the time and with no bearing on the current recovery window.

## Contact

Queries about station 766 are best raised in the network chat before you commit a booking.
