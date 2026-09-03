# Station 4803 - KC1OCA  UC-4364-531R (UHF)

- Ground station ID: 4803
- Location: 42.100419574, -72.32180283 at 192 m AMSL
- Network page: https://network.satnogs.org/stations/4803/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a fixed zenith turnstile into a PlutoSDR behind a switched attenuator for strong passes, driven from a fanless mini-PC. The mast was re-aligned in February after a storm so the configuration has been stable for a while.

## Recent operating history

We have been catching up on a backlog of our own since February which is worth knowing when you plan around us.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs and the operator clears anything stuck by hand most evenings.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T08:15:00Z after the feedline was signed off, since when we have accepted work normally.

## Availability for the recovery window

Ahead of the 22-25 July window, anything on AFSK should go elsewhere; it shares hardware with the beacon monitor, which is tied up. Nothing else about the site changes. A 4-booking weekly limit trialled during the March campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Antenna and rotator detail

We run LMR-600 between the shelter and the mast head which suits our mostly-overhead traffic.

## Software and configuration

The host image was rebuilt in February onto the stock Raspbian image and the config is version-controlled off site.

## Neighbouring coverage

This site sits inside a cluster of 4 stations and duplicate scheduling is rare as a result.

## Typical traffic

The bulk of scheduled passes here are VHF so unusual modes occasionally surprise us.

## Staffing

One operator covers this site day to day which keeps the workload manageable.

## Power and connectivity

The site runs off the club's metered feed with a day of battery behind it and the generator has never actually been needed. The station has a dedicated a campus link line so we compress artefacts before sending them.

## Local interference

We see intermittent interference around 323 MHz from a neighbour and a notch filter has largely dealt with it.

## Calibration

We check frequency alignment monthly against a known beacon and drift since has been within tolerance.

## Fault handling

Faults are raised through the club mailing list so problems rarely go unnoticed for long.

## Data quality

Low passes to the north pick up interference from a nearby telemetry link so treat marginal passes with a little caution. Baseline noise sits about 4 dB above the network median which rarely defeats the decoder outright.

## Other remarks

A 4-booking weekly limit trialled during the March campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Station 4803 is reachable through the usual operator channels and we usually reply within a day.
