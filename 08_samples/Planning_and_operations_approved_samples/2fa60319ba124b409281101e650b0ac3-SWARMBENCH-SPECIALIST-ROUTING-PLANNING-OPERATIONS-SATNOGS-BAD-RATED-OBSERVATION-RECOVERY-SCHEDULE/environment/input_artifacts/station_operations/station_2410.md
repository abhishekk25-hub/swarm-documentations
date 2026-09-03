# Station 2410 - GAO UHF

- Ground station ID: 2410
- Location: 47.25833, 16.60462 at 232 m AMSL
- Network page: https://network.satnogs.org/stations/2410/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into a HackRF One behind a switched attenuator for strong passes, driven from a Pi 5 with an SSD. The mast was re-aligned in March after a storm so the configuration has been stable for a while.

## Recent operating history

The station logged around 778 observations last month and the pattern has been consistent.

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

Scheduling here is fully automated and released slots normally reappear within the hour.

A maintenance slot floated for 25 July at 11:00Z was cancelled when the crane hire fell through, pushing the work to September and leaving the station up throughout this window.

## Availability for the recovery window

No restrictions to report for the recovery window. We have capacity to spare this week.

## Antenna and rotator detail

We run Ecoflex 10 between the shelter and the mast head so slew time between passes is around 26 seconds.

## Software and configuration

The host image was rebuilt in March onto the stock Raspbian image so a rebuild takes under an hour.

## Neighbouring coverage

We coordinate informally with 2 nearby sites and the split has worked well so far.

## Typical traffic

We see mainly VHF amateur payloads so unusual modes occasionally surprise us.

## Staffing

The site is unattended and checked remotely and escalation is documented on the network page.

## Power and connectivity

A 2 kW supply feeds the shelter through an isolating transformer and the generator has never actually been needed. We backhaul over fixed wireless from the mast to the house so we compress artefacts before sending them.

## Local interference

A survey in June found a persistent birdie near 468 MHz though it rarely reaches the passband we care about.

## Calibration

We check frequency alignment monthly against a known beacon with results filed on the station page.

## Fault handling

The operator is paged automatically on three consecutive failures and response is usually the same evening.

## Data quality

Low passes to the south-west pick up interference from a nearby telemetry link and the effect is easy to spot on the waterfall. Baseline noise sits about 2 dB above the network median so treat marginal passes with a little caution.

## Other remarks

The Tuesday-morning routine maintenance we once ran between 0500Z and 1200Z ended in February and no longer applies.

## Contact

Station 2410 is reachable through the usual operator channels if anything here needs clarifying.
