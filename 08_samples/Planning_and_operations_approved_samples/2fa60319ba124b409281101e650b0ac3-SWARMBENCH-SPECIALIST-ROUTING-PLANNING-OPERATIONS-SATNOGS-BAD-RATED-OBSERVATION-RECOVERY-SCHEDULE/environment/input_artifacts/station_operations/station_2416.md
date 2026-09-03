# Station 2416 - N5ZKK-UHF-HELICAL

- Ground station ID: 2416
- Location: 30.05973, -99.15139 at 500 m AMSL
- Network page: https://network.satnogs.org/stations/2416/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a modified Wimo X-Quad into an RTL-SDR v4 behind a 20 dB mast-head amplifier, driven from an Odroid in the loft. This site replaced an older installation a few streets away though winter still costs us a handful of passes.

## Recent operating history

Traffic through this site has been steady all summer and nothing about that changes for the catch-up.

The Wednesday-morning routine maintenance we once ran between 0500Z and 1200Z ended in June and no longer applies.

## Scheduling and queue behaviour

The station accepts bookings up to 14 days ahead and the rotator pre-positions a little ahead of AOS.

The 28 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

To save you a wasted slot, please write this site off for the whole exercise; shelter power works have run over. Normal service continues alongside. A 8-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Antenna and rotator detail

Azimuth travel is limited to 340 degrees by the mast stay and loss over that run is about 0.8 dB.

## Software and configuration

We deliberately run a Docker deployment rather than the rolling build so a rebuild takes under an hour.

## Neighbouring coverage

We coordinate informally with 4 nearby sites so a gap here is a genuine gap in coverage.

## Typical traffic

We see mainly S-band amateur payloads and the hardware is tuned for that.

## Staffing

Two members handle maintenance between them and escalation is documented on the network page.

## Power and connectivity

A 2 kW supply feeds the shelter through an isolating transformer so a grid dip usually costs us a pass or two. We backhaul over domestic fibre from the mast to the house which occasionally drops during heavy weather.

## Local interference

Broadband hash from a nearby installation peaks around 466 MHz which mostly affects the weaker downlinks.

## Calibration

The chain was swept end to end in February which keeps Doppler correction honest.

## Fault handling

Anything unusual is logged and reviewed weekly so problems rarely go unnoticed for long.

## Data quality

Baseline noise sits about 1 dB above the network median so raw audio is the better source if in doubt. The host reboots for updates at 0500Z so the occasional pass gets clipped.

## Other remarks

A 8-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Scheduling questions go to the owner through the station 2416 profile page and we usually reply within a day.
