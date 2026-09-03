# Station 4924 - Wroclaw Ground Station

- Ground station ID: 4924
- Location: 51.078029, 17.037027 at 139 m AMSL
- Network page: https://network.satnogs.org/stations/4924/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into an RTL-SDR Blog v3 behind a bias-tee LNA at the mast head, driven from a rack-mounted NUC. This site replaced an older installation a few streets away so the configuration has been stable for a while.

## Recent operating history

We have been catching up on a backlog of our own since May so expect the usual throughput.

The Friday-morning routine maintenance we once ran between 0600Z and 1200Z ended in February and no longer applies.

## Scheduling and queue behaviour

We run a conservative queue depth of about 30 though back-to-back passes on opposite azimuths can lose a few seconds.

Our sister site 4934 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

For planning purposes, please cap us at 1 make-good bookings; beyond that the upload queue backs up for days. Anything outside that scope is fine.

## Antenna and rotator detail

We run RG-213 between the shelter and the mast head which is adequate for the passes we take.

## Software and configuration

The site runs a Docker deployment pinned to a known-good release and the config is version-controlled off site.

## Neighbouring coverage

The nearest other station is roughly 336 km away which matters when we go offline.

## Typical traffic

The bulk of scheduled passes here are S-band and the hardware is tuned for that.

## Staffing

A rota of 4 keyholders shares the work which keeps the workload manageable.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 2 kW inverter so brownouts show up as gaps rather than failures. We backhaul over ADSL from the mast to the house and transfers finish well inside the pass gap.

## Local interference

A survey in May found a persistent birdie near 263 MHz though it rarely reaches the passband we care about.

## Calibration

The receiver was last calibrated against a GPSDO in February with results filed on the station page.

## Fault handling

The station reports its own health to a dashboard and response is usually the same evening.

## Data quality

Waterfall uploads occasionally stall on the domestic link which rarely defeats the decoder outright. Recordings are archived locally for 14 days and uploaded on completion and the effect is easy to spot on the waterfall.

## Other remarks

A maintenance slot floated for 23 July at 19:00Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Queries about station 4924 are best raised in the network chat and we are happy to discuss alternatives.
