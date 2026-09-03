# Station 2097 - KU4YJ

- Ground station ID: 2097
- Location: 34.71426, -86.75529 at 238 m AMSL
- Network page: https://network.satnogs.org/stations/2097/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into a PlutoSDR behind a helical bandpass filter, driven from an old ThinkPad in the garage. Weather exposure is the main limiting factor here with no changes planned before the autumn.

## Recent operating history

The station logged around 673 observations last month so our numbers should look familiar.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-18T04:15:00Z after the feedline was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 15 minutes and anything unusual is reviewed before it runs.

A maintenance slot floated for 23 July at 20:00Z was cancelled when the contractor fell through, pushing the work to August and leaving the station up throughout this window.

## Availability for the recovery window

In short, if the pass tops out under 48 degrees we would rather you gave it to someone else; low-angle multipath here is severe. Everything else is unaffected. An earlier revision of this note listed a booking freeze, lifted at 2026-07-18T04:15:00Z after the feedline was signed off, since when we have accepted work normally.

## Antenna and rotator detail

The feed is a balun at the driven element with a measured VSWR under 1.3 and loss over that run is about 2.1 dB.

## Software and configuration

Scheduling is driven by satnogs-client 1.8 with local patches which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the south so handing work over is usually straightforward.

## Typical traffic

Most of our traffic is S-band weather and cubesat work which shapes how the antenna was built.

## Staffing

A rota of 3 keyholders shares the work so response outside evenings can be slow.

## Power and connectivity

The site runs off the club's metered feed with 40 minutes of battery behind it and the generator has never actually been needed. The site uses ADSL with a fixed address though the monthly allowance is not generous.

## Local interference

A survey in June found a persistent birdie near 330 MHz and a notch filter has largely dealt with it.

## Calibration

We check frequency alignment monthly against a known beacon though we plan another check before winter.

## Fault handling

The operator is paged automatically on three consecutive failures and response is usually the same evening.

## Data quality

Baseline noise sits about 1 dB above the network median though nothing has needed intervention this quarter. Low passes to the north pick up interference from a nearby telemetry link so raw audio is the better source if in doubt.

## Other remarks

A 6-booking weekly limit trialled during the March campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Reach the operator of station 2097 on the community forum though replies can be slow at weekends.
