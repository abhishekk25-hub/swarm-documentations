# Station 3925 - UT4UYF/P

- Ground station ID: 3925
- Location: 50.559, 29.914 at 145 m AMSL
- Network page: https://network.satnogs.org/stations/3925/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a fixed zenith turnstile into an Airspy Mini behind a 20 dB mast-head amplifier, driven from an Odroid in the loft. Weather exposure is the main limiting factor here though winter still costs us a handful of passes.

## Recent operating history

This site mostly serves the eastern horizon which is worth knowing when you plan around us.

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

Job intake is manual-review so a booked pass runs unless the site itself is unavailable.

A maintenance slot floated for 23 July at 00:00Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Availability for the recovery window

The main thing is that anything peaking below 40 degrees is unusable here; nearby buildings shadow anything shallow. Other than that we are fully available. An earlier revision of this note listed a booking freeze, lifted at 2026-07-13T11:00:00Z after the feedline was signed off, since when we have accepted work normally. One constraint from our side: we can commit to a limit of 3 extra passes; beyond that the upload queue backs up for days. We remain open either side of it.

## Antenna and rotator detail

The whole assembly was re-tensioned after the June storms though it wants re-checking each spring.

## Software and configuration

The host image was rebuilt in June onto a Docker deployment so a rebuild takes under an hour.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the north and the split has worked well so far.

## Typical traffic

The bulk of scheduled passes here are S-band with the rest spread across other bands.

## Staffing

Two members handle maintenance between them with the club providing cover during holidays.

## Power and connectivity

Everything here is fed from a rooftop solar array with grid tie via a residual-current breaker and the generator has never actually been needed. The station has a dedicated a 4G modem line though the monthly allowance is not generous.

## Local interference

The local noise floor sits worst toward the west and it is documented in our station notes upstream.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source and nothing has moved since.

## Fault handling

The operator is paged automatically on three consecutive failures and the log is public on request.

## Data quality

Decoder success here has run around 93 per cent over the past year though nothing has needed intervention this quarter. Low passes to the east pick up interference from a nearby telemetry link which we are slowly working to improve.

## Other remarks

A 3-booking weekly limit trialled during the May campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Station 3925 is reachable through the usual operator channels if anything here needs clarifying.
