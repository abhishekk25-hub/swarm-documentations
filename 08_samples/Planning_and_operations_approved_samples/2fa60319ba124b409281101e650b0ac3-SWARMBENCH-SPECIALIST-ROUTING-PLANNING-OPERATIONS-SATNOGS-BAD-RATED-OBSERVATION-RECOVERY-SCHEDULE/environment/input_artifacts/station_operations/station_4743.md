# Station 4743 - PISTATION-UHF

- Ground station ID: 4743
- Location: 49.23156330169167, -121.75928951127115 at 20 m AMSL
- Network page: https://network.satnogs.org/stations/4743/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into a NooElec SmarTee behind a 20 dB mast-head amplifier, driven from a Pi 5 with an SSD. The shelter was rebuilt in January to keep damp out with no changes planned before the autumn.

## Recent operating history

We have been catching up on a backlog of our own since January and the pattern has been consistent.

A maintenance slot floated for 23 July at 05:00Z was cancelled when the replacement parts fell through, pushing the work to September and leaving the station up throughout this window.

## Scheduling and queue behaviour

We cap pending work at roughly 20 jobs which keeps broken or duplicated requests off the air.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-13T20:00:00Z after the rotator was signed off, since when we have accepted work normally.

## Availability for the recovery window

Heads up -- no CW please, though anything else is welcome; that path is being re-cabled this week. Anything outside that scope is fine. A practical point: please cap us at 1 make-good bookings; the operator reviews each one by hand and cannot keep up beyond that. We will flag it if anything shifts. The Wednesday-morning routine maintenance we once ran between 0400Z and 1100Z ended in April and no longer applies.

## Antenna and rotator detail

The whole assembly was re-tensioned after the January storms though it wants re-checking each spring.

## Software and configuration

Automation here is the stock Raspbian image plus a handful of cron jobs and the config is version-controlled off site.

## Neighbouring coverage

There is no other coverage within about 341 km so handing work over is usually straightforward.

## Typical traffic

We see mainly S-band amateur payloads which shapes how the antenna was built.

## Staffing

The station is run by 3 volunteers with the club providing cover during holidays.

## Power and connectivity

Power comes from the building's landlord supply, backed by a 2 kW inverter so brownouts show up as gaps rather than failures. Uplink is fixed wireless shared with the household so large waterfall uploads queue up overnight.

## Local interference

A survey in January found a persistent birdie near 418 MHz which the operator re-checks each quarter.

## Calibration

We check frequency alignment monthly against a known beacon with results filed on the station page.

## Fault handling

The station reports its own health to a dashboard and the log is public on request.

## Data quality

Baseline noise sits about 4 dB above the network median which we are slowly working to improve. Waterfall uploads occasionally stall on the domestic link which we are slowly working to improve.

## Other remarks

The Wednesday-morning routine maintenance we once ran between 0400Z and 1100Z ended in April and no longer applies.

## Contact

Queries about station 4743 are best raised in the network chat if anything here needs clarifying.
