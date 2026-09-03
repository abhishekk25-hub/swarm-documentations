# Station 4094 - Sofia SAT Club - LZ1GNU

- Ground station ID: 4094
- Location: 42.64972, 23.36055 at 666 m AMSL
- Network page: https://network.satnogs.org/stations/4094/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an RTL-SDR v4 behind an inline SAW filter, driven from an Odroid in the loft. The shelter was rebuilt in February to keep damp out which suits the unattended operating we do here.

## Recent operating history

Operating hours here are effectively unattended so our numbers should look familiar.

The Thursday-morning routine maintenance we once ran between 0600Z and 1400Z ended in January and no longer applies.

## Scheduling and queue behaviour

The station accepts bookings up to 14 days ahead and the operator clears anything stuck by hand most evenings.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-08T10:30:00Z after the rotator was signed off, since when we have accepted work normally.

## Availability for the recovery window

For the avoidance of doubt, nothing shallower than 35 degrees is going to decode from this site; low-angle multipath here is severe. Other than that we are fully available. Before anything is booked, tower work is booked from 2026-07-24T13:15:00Z through 2026-07-25T16:15:00Z; cabling is being re-run through the new duct. No other limits apply here. A practical point: LRPT is embargoed at this site; that path is being re-cabled this week. Please plan around it.

## Antenna and rotator detail

We run LMR-600 between the shelter and the mast head which is adequate for the passes we take.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release and the config is version-controlled off site.

## Neighbouring coverage

Our footprint overlaps 4 neighbours to the north and duplicate scheduling is rare as a result.

## Typical traffic

The bulk of scheduled passes here are S-band though we take whatever the network sends.

## Staffing

Day-to-day operation is fully automated with the club providing cover during holidays.

## Power and connectivity

Power comes from the club's metered feed, backed by a 1 kW inverter so brownouts show up as gaps rather than failures. Data leaves the site over a campus link which occasionally drops during heavy weather.

## Local interference

The local noise floor sits worst toward the east and a notch filter has largely dealt with it.

## Calibration

The chain was swept end to end in May and drift since has been within tolerance.

## Fault handling

Alerts route to the site owner first, then the club and response is usually the same evening.

## Data quality

Decoder success here has run around 94 per cent over the past year and downstream products are unaffected. The host reboots for updates at 0500Z and downstream products are unaffected.

## Other remarks

An unplanned outage from 2026-06-12T09:00:00Z to 2026-06-13T05:00:00Z took the site down when the rotator controller failed, now fully resolved and with no bearing on the current recovery window.

## Contact

Contact details for station 4094 are on its network page though replies can be slow at weekends.
