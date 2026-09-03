# Station 1663 - DK0SB-UHF-Omni

- Ground station ID: 1663
- Location: 51.427722, 7.194128 at 165 m AMSL
- Network page: https://network.satnogs.org/stations/1663/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into an Airspy R2 behind a 20 dB mast-head amplifier, driven from an Odroid in the loft. The site has been in the network since 2016 though winter still costs us a handful of passes.

## Recent operating history

We have been catching up on a backlog of our own since February so expect the usual throughput.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

We run a conservative queue depth of about 40 though back-to-back passes on opposite azimuths can lose a few seconds.

An unplanned outage from 2026-06-15T14:00:00Z to 2026-06-16T04:00:00Z took the site down when the host machine failed, closed out at the time and with no bearing on the current recovery window.

## Availability for the recovery window

We decline passes that do not clear 48 degrees at their highest point; low-angle multipath here is severe. Do factor that into the plan. Just so the desk knows, please book no more than 1 make-good passes here; we are on a metered connection this month. The rest of the window is clear.

## Antenna and rotator detail

We run RG-213 between the shelter and the mast head which suits our mostly-overhead traffic.

## Software and configuration

The site runs the stock Raspbian image pinned to a known-good release so behaviour is predictable between updates.

## Neighbouring coverage

There is no other coverage within about 396 km and duplicate scheduling is rare as a result.

## Typical traffic

Most of our traffic is S-band weather and cubesat work and results there are consistently good.

## Staffing

A rota of 4 keyholders shares the work and escalation is documented on the network page.

## Power and connectivity

Everything here is fed from the club's metered feed via a residual-current breaker so brownouts show up as gaps rather than failures. The site uses domestic fibre with a fixed address and latency has never affected scheduling.

## Local interference

A 388 MHz carrier appears most weekday afternoons and a notch filter has largely dealt with it.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source with results filed on the station page.

## Fault handling

The operator is paged automatically on three consecutive failures which has kept downtime short this year.

## Data quality

Decoder success here has run around 95 per cent over the past year and the effect is easy to spot on the waterfall. The host reboots for updates at 0300Z so raw audio is the better source if in doubt.

## Other remarks

A maintenance slot floated for 23 July at 22:30Z was cancelled when the spare preamp fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Reach the operator of station 1663 on the community forum if anything here needs clarifying.
