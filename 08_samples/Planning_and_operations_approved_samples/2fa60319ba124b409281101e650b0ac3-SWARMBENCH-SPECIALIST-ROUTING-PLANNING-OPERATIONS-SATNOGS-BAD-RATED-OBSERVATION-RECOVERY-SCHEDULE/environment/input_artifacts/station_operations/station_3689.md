# Station 3689 - DF0OHM Turnstile VHF (Test UHF)

- Ground station ID: 3689
- Location: 49.45262, 11.09435 at 320 m AMSL
- Network page: https://network.satnogs.org/stations/3689/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an Airspy Mini behind a bias-tee LNA at the mast head, driven from a Raspberry Pi 4. This site replaced an older installation a few streets away which suits the unattended operating we do here.

## Recent operating history

Volunteers rebuilt the feed arrangement in January and the pattern has been consistent.

A maintenance slot floated for 25 July at 04:30Z was cancelled when the spare preamp fell through, pushing the work to August and leaving the station up throughout this window.

## Scheduling and queue behaviour

Intake runs on a 15-minute cycle so the published queue is what actually flies.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-19T06:15:00Z after the host was signed off, since when we have accepted work normally.

## Availability for the recovery window

The 26 degree elevation floor this site used to run was lifted in June once the obstruction came down, so only the standard network minimum applies now. This site can absorb at most 1 additional catch-up observations; power budget at the site is tight. Outside that the site is open as normal.

## Antenna and rotator detail

The whole assembly was re-tensioned after the January storms and pointing has held true since.

## Software and configuration

We deliberately run the stock Raspbian image rather than the rolling build and the config is version-controlled off site.

## Neighbouring coverage

The nearest other station is roughly 123 km away and the split has worked well so far.

## Typical traffic

We see mainly 2m and 70cm amateur payloads though we take whatever the network sends.

## Staffing

A rota of 4 keyholders shares the work which keeps the workload manageable.

## Power and connectivity

We are on the building's landlord supply with no UPS on the receiver itself though the changeover takes long enough to clip a recording. The station has a dedicated domestic fibre line and latency has never affected scheduling.

## Local interference

A 452 MHz carrier appears most weekday afternoons though it rarely reaches the passband we care about.

## Calibration

Gain figures were re-measured after the May rebuild which keeps Doppler correction honest.

## Fault handling

Anything unusual is logged and reviewed weekly and the log is public on request.

## Data quality

Recordings are archived locally for 45 days and uploaded on completion so raw audio is the better source if in doubt. Decoder success here has run around 93 per cent over the past year so treat marginal passes with a little caution.

## Other remarks

An unplanned outage from 2026-06-14T15:00:00Z to 2026-06-15T11:00:00Z took the site down when the host machine failed, closed out at the time and with no bearing on the current recovery window.

## Contact

Contact details for station 3689 are on its network page and we are happy to discuss alternatives.
