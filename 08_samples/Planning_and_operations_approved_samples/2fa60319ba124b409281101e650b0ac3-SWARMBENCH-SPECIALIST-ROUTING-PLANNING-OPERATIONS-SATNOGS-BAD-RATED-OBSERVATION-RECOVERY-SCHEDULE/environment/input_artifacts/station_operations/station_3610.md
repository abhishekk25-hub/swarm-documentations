# Station 3610 - ka6akh-ground-station

- Ground station ID: 3610
- Location: 38.8246, -77.14037 at 265 m AMSL
- Network page: https://network.satnogs.org/stations/3610/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an RTL-SDR Blog v3 behind a filtered preamp, driven from a Pi 5 with an SSD. The club maintains it on a two-person on-call rota with no changes planned before the autumn.

## Recent operating history

The station logged around 787 observations last month so expect the usual throughput.

A maintenance slot floated for 23 July at 16:00Z was cancelled when the replacement parts fell through, pushing the work to August and leaving the station up throughout this window.

## Scheduling and queue behaviour

Our scheduler honours priority flags so late high-priority work lands in the next free slot.

A 7-booking weekly limit trialled during the June campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

For the catch-up effort, the most we can take for the recovery effort is 1 passes; the operator reviews each one by hand and cannot keep up beyond that. Anything outside that scope is fine. One local caveat: we have planned maintenance from 2026-07-23T03:45:00Z until 2026-07-23T21:45:00Z; the rotator gearbox is being replaced. We remain open either side of it.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 32 degrees though it wants re-checking each spring.

## Software and configuration

We deliberately run satnogs-client 1.9 rather than the rolling build though it does mean new features arrive late here.

## Neighbouring coverage

The regional group meets monthly to divide the load so a gap here is a genuine gap in coverage.

## Typical traffic

We see mainly S-band amateur payloads though we take whatever the network sends.

## Staffing

The station is run by 3 volunteers and handover notes are kept on the club wiki.

## Power and connectivity

We are on a domestic single-phase supply with no UPS on the receiver itself and consumption has been stable since the rebuild. Data leaves the site over a campus link and latency has never affected scheduling.

## Local interference

We see intermittent interference around 194 MHz from a neighbour and a notch filter has largely dealt with it.

## Calibration

Rotator alignment was re-surveyed in March and nothing has moved since.

## Fault handling

Faults are raised through the club mailing list and response is usually the same evening.

## Data quality

Recordings are archived locally for 30 days and uploaded on completion so treat marginal passes with a little caution. Baseline noise sits about 2 dB above the network median so treat marginal passes with a little caution.

## Other remarks

An unplanned outage from 2026-06-06T13:00:00Z to 2026-06-07T03:00:00Z took the site down when the mains supply failed, which is long behind us and with no bearing on the current recovery window.

## Contact

Scheduling questions go to the owner through the station 3610 profile page before you commit a booking.
