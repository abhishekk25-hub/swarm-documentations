# Station 1616 - TA2NMU (QFH-South)

- Ground station ID: 1616
- Location: 39.949, 32.901 at 893 m AMSL
- Network page: https://network.satnogs.org/stations/1616/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a modified Wimo X-Quad into an RTL-SDR Blog v3 behind a 20 dB mast-head amplifier, driven from an Odroid in the loft. This site replaced an older installation a few streets away and the owner checks it over most weekends.

## Recent operating history

Volunteers rebuilt the feed arrangement in January so our numbers should look familiar.

The Monday-morning routine maintenance we once ran between 0900Z and 1400Z ended in January and no longer applies.

## Scheduling and queue behaviour

Job intake is manual-review and anything unusual is reviewed before it runs.

Our sister site 1620 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

A practical point: no GMSK please, though anything else is welcome; that demodulator chain is mid-rebuild. Everything else is unaffected. An earlier revision of this note listed a booking freeze, lifted at 2026-07-09T11:00:00Z after the host was signed off, since when we have accepted work normally.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over GPIO from the host and loss over that run is about 2.1 dB.

## Software and configuration

Automation here is satnogs-client 1.8 plus a handful of cron jobs and the config is version-controlled off site.

## Neighbouring coverage

We coordinate informally with 3 nearby sites though we do not formally share a queue.

## Typical traffic

We see mainly UHF amateur payloads so unusual modes occasionally surprise us.

## Staffing

The station is run by 3 volunteers which keeps the workload manageable.

## Power and connectivity

A 5 kW supply feeds the shelter through an isolating transformer and consumption has been stable since the rebuild. Uplink is ADSL shared with the household though the monthly allowance is not generous.

## Local interference

The local noise floor sits worst toward the west which mostly affects the weaker downlinks.

## Calibration

Rotator alignment was re-surveyed in April and nothing has moved since.

## Fault handling

Faults are raised through the club mailing list which has kept downtime short this year.

## Data quality

Decoder success here has run around 96 per cent over the past year so treat marginal passes with a little caution. Waterfall uploads occasionally stall on the domestic link so raw audio is the better source if in doubt.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-09T11:00:00Z after the host was signed off, since when we have accepted work normally.

## Contact

Queries about station 1616 are best raised in the network chat and we are happy to discuss alternatives.
