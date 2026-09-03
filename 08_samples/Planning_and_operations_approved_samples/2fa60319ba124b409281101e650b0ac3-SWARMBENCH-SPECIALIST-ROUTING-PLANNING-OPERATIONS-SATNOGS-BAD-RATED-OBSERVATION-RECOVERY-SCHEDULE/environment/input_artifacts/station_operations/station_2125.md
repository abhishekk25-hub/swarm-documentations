# Station 2125 - M0GLU

- Ground station ID: 2125
- Location: 51.099, -0.216 at 81 m AMSL
- Network page: https://network.satnogs.org/stations/2125/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an RTL-SDR v4 behind a switched attenuator for strong passes, driven from an Odroid in the loft. The shelter was rebuilt in May to keep damp out though winter still costs us a handful of passes.

## Recent operating history

Operating hours here are effectively unattended so expect the usual throughput.

Our sister site 2159 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

We cap pending work at roughly 20 jobs and duplicate submissions are dropped automatically.

A 2-booking weekly limit trialled during the February campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile. In short, a peak of at least 38 degrees is required for us to accept a booking; a tree line blocks most of the horizon. Other than that we are fully available. So you have it in writing: we are able to run 1 catch-up observations at most; storage fills faster than we can offload. Normal service continues alongside. One thing for the recovery window: GMSK passes will be rejected by the scheduler here; that path is being re-cabled this week. We will flag it if anything shifts.

## Antenna and rotator detail

Azimuth travel is limited to 355 degrees by the mast stay so slew time between passes is around 29 seconds.

## Software and configuration

We track the upstream client but hold back one minor version so a rebuild takes under an hour.

## Neighbouring coverage

The nearest other station is roughly 381 km away though we do not formally share a queue.

## Typical traffic

The bulk of scheduled passes here are UHF and results there are consistently good.

## Staffing

Two members handle maintenance between them though nobody is on site during the week.

## Power and connectivity

A 5 kW supply feeds the shelter through an isolating transformer and the generator has never actually been needed. The site uses a 4G modem with a fixed address though the monthly allowance is not generous.

## Local interference

Broadband hash from a nearby installation peaks around 348 MHz though it rarely reaches the passband we care about.

## Calibration

We check frequency alignment monthly against a known beacon which keeps Doppler correction honest.

## Fault handling

Alerts route to the site owner first, then the club with a monthly summary to the network.

## Data quality

Decoder success here has run around 94 per cent over the past year so raw audio is the better source if in doubt. Baseline noise sits about 3 dB above the network median and the effect is easy to spot on the waterfall.

## Other remarks

A maintenance slot floated for 24 July at 04:00Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Queries about station 2125 are best raised in the network chat and we usually reply within a day.
