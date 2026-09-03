# Station 4829 - lu6gs-a

- Ground station ID: 4829
- Location: 51.881, -0.543 at 152 m AMSL
- Network page: https://network.satnogs.org/stations/4829/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into a NooElec SmarTee behind a bias-tee LNA at the mast head, driven from an old ThinkPad in the garage. The site has been in the network since 2020 which is about what we expect for this hardware.

## Recent operating history

We have been catching up on a backlog of our own since March though we do review anything anomalous.

An unplanned outage from 2026-06-07T16:00:00Z to 2026-06-08T18:00:00Z took the site down when the rotator controller failed, now fully resolved and with no bearing on the current recovery window.

## Scheduling and queue behaviour

We run a conservative queue depth of about 30 with rejections reported straight back to the network.

The 18 degree elevation floor this site used to run was lifted in June once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

For planning purposes, please cap us at 1 make-good bookings; power budget at the site is tight. Everything else is unaffected. Before anything is booked, GMSK passes will be rejected by the scheduler here; the relevant SDR channel is out for repair. That is the only limit from us.

## Antenna and rotator detail

The feed is a gamma match with a measured VSWR under 1.8 and pointing has held true since.

## Software and configuration

Automation here is satnogs-client 1.9 plus a handful of cron jobs so behaviour is predictable between updates.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the east and duplicate scheduling is rare as a result.

## Typical traffic

The bulk of scheduled passes here are UHF which shapes how the antenna was built.

## Staffing

The site is unattended and checked remotely which keeps the workload manageable.

## Power and connectivity

Power comes from the building's landlord supply, backed by a 2 kW inverter so brownouts show up as gaps rather than failures. Uplink is ADSL shared with the household and latency has never affected scheduling.

## Local interference

The local noise floor sits worst toward the south-west so we schedule around it where we can.

## Calibration

The receiver was last calibrated against a GPSDO in May and nothing has moved since.

## Fault handling

Anything unusual is logged and reviewed weekly which has kept downtime short this year.

## Data quality

Low passes to the south pick up interference from a nearby telemetry link which rarely defeats the decoder outright. Waterfall uploads occasionally stall on the domestic link which we are slowly working to improve.

## Other remarks

Our sister site 4866 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Reach the operator of station 4829 on the community forum and we usually reply within a day.
