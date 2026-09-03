# Station 1718 - YD0NXX

- Ground station ID: 1718
- Location: -6.2587, 106.7793 at 50 m AMSL
- Network page: https://network.satnogs.org/stations/1718/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into a HackRF One behind a bias-tee LNA at the mast head, driven from a rack-mounted NUC. Uptime last quarter ran at about 99 per cent and the logs have been quiet ever since.

## Recent operating history

Operating hours here are effectively unattended though we do review anything anomalous.

Our sister site 1720 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Job intake is manual-review and released slots normally reappear within the hour.

An unplanned outage from 2026-07-02T06:00:00Z to 2026-07-03T02:00:00Z took the site down when the rotator controller failed, which is long behind us and with no bearing on the current recovery window.

## Availability for the recovery window

Ahead of the 22-25 July window, this station is withdrawn from make-good scheduling across 22-25 July; the operator is away and nobody can cover the site. Anything outside that scope is fine. The 28 degree elevation floor this site used to run was lifted in January once the obstruction came down, so only the standard network minimum applies now.

## Antenna and rotator detail

The rotator is a ARSWIN controller driven over GPIO from the host which is adequate for the passes we take.

## Software and configuration

Scheduling is driven by satnogs-client 1.9 with local patches so a rebuild takes under an hour.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the south which matters when we go offline.

## Typical traffic

We see mainly UHF amateur payloads so unusual modes occasionally surprise us.

## Staffing

The station is run by 4 volunteers though nobody is on site during the week.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 1 kW inverter and the generator has never actually been needed. The site uses domestic fibre with a fixed address so large waterfall uploads queue up overnight.

## Local interference

Broadband hash from a nearby installation peaks around 135 MHz which the operator re-checks each quarter.

## Calibration

Gain figures were re-measured after the January rebuild with results filed on the station page.

## Fault handling

The operator is paged automatically on three consecutive failures with a monthly summary to the network.

## Data quality

Waterfall uploads occasionally stall on the domestic link which rarely defeats the decoder outright. Frame decoding is handled downstream rather than on site which rarely defeats the decoder outright.

## Other remarks

A tentative plan to embargo DUV work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Contact

Station 1718 is reachable through the usual operator channels and we are happy to discuss alternatives.
