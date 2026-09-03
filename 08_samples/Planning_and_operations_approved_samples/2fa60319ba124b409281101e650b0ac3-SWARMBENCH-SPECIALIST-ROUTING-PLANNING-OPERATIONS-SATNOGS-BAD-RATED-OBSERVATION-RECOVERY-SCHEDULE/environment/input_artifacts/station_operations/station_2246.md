# Station 2246 - HB9FXX Komodo Dome

- Ground station ID: 2246
- Location: 52.30446825839176, 19.16926930632765 at 250 m AMSL
- Network page: https://network.satnogs.org/stations/2246/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into an RTL-SDR v4 behind a switched attenuator for strong passes, driven from a Pi 5 with an SSD. The club maintains it on a two-person on-call rota though winter still costs us a handful of passes.

## Recent operating history

Traffic through this site has been steady all summer which is worth knowing when you plan around us.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

The station accepts bookings up to 14 days ahead with a short grace period for cancellations.

A 5-booking weekly limit trialled during the February campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

Ahead of the 22-25 July window, we decline passes that do not clear 48 degrees at their highest point; reflections off the water confuse anything shallow. We will flag it if anything shifts. One constraint from our side: an engineer is on site from 07:30Z on 22 July to 18:30Z on 22 July and the chain will be broken; grounding work needs the whole chain isolated. Everything else is unaffected.

## Antenna and rotator detail

Azimuth travel is limited to 340 degrees by the mast stay and pointing has held true since.

## Software and configuration

Automation here is the stock Raspbian image plus a handful of cron jobs so behaviour is predictable between updates.

## Neighbouring coverage

There is no other coverage within about 145 km and duplicate scheduling is rare as a result.

## Typical traffic

Most of our traffic is 2m and 70cm weather and cubesat work and results there are consistently good.

## Staffing

The site is unattended and checked remotely and escalation is documented on the network page.

## Power and connectivity

A 1 kW supply feeds the shelter through an isolating transformer so brownouts show up as gaps rather than failures. Connectivity is a 4G modem, which is the weak point here so we compress artefacts before sending them.

## Local interference

A survey in June found a persistent birdie near 404 MHz which mostly affects the weaker downlinks.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source which keeps Doppler correction honest.

## Fault handling

Anything unusual is logged and reviewed weekly and response is usually the same evening.

## Data quality

Baseline noise sits about 1 dB above the network median so the occasional pass gets clipped. Frame decoding is handled downstream rather than on site and the effect is easy to spot on the waterfall.

## Other remarks

A maintenance slot floated for 23 July at 23:00Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Reach the operator of station 2246 on the community forum and we are happy to discuss alternatives.
