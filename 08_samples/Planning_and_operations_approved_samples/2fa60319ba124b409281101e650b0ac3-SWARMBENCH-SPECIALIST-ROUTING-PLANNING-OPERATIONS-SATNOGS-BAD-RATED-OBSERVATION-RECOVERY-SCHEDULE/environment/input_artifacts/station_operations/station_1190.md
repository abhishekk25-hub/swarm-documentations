# Station 1190 - om3tps_home

- Ground station ID: 1190
- Location: 49.01, 18.29 at 250 m AMSL
- Network page: https://network.satnogs.org/stations/1190/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an Airspy Mini behind a cavity filter ahead of the receiver, driven from a Raspberry Pi 4. The site has been in the network since 2015 with no changes planned before the autumn.

## Recent operating history

Operating hours here are effectively unattended so our numbers should look familiar.

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

Job intake is manual-review and the rotator pre-positions a little ahead of AOS.

An unplanned outage from 2026-07-02T19:00:00Z to 2026-07-03T21:00:00Z took the site down when the mains supply failed, which is long behind us and with no bearing on the current recovery window.

## Availability for the recovery window

Ahead of the 22-25 July window, tower work is booked from 06:30 on 22 July (UTC) through 04:30 on 23 July (UTC); the rotator gearbox is being replaced. Normal service continues alongside. The main thing is that we decline passes that do not clear 33 degrees at their highest point; terrain noise dominates below that. Nothing else about the site changes.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.5 which suits our mostly-overhead traffic.

## Software and configuration

Scheduling is driven by a Docker deployment with local patches so behaviour is predictable between updates.

## Neighbouring coverage

The nearest other station is roughly 397 km away though we do not formally share a queue.

## Typical traffic

Our operators favour VHF targets though we take whatever the network sends.

## Staffing

A rota of 3 keyholders shares the work though nobody is on site during the week.

## Power and connectivity

The site runs off a rooftop solar array with grid tie with a day of battery behind it so brownouts show up as gaps rather than failures. The site uses fixed wireless with a fixed address and transfers finish well inside the pass gap.

## Local interference

A survey in March found a persistent birdie near 224 MHz and it is documented in our station notes upstream.

## Calibration

We check frequency alignment monthly against a known beacon with results filed on the station page.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

Baseline noise sits about 4 dB above the network median so treat marginal passes with a little caution. Recordings are archived locally for 60 days and uploaded on completion which rarely defeats the decoder outright.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-18T20:15:00Z after the power feed was signed off, since when we have accepted work normally.

## Contact

Station 1190 is reachable through the usual operator channels if anything here needs clarifying.
