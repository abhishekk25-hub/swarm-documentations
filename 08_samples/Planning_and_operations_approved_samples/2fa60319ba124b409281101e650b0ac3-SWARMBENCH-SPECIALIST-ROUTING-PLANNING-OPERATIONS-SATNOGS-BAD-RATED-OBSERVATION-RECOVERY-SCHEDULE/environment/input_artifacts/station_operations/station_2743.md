# Station 2743 - AldingaBeach Ground Station

- Ground station ID: 2743
- Location: -35.279, 138.453 at 20 m AMSL
- Network page: https://network.satnogs.org/stations/2743/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a twin-band vertical with a phasing harness into an RTL-SDR v4 behind a cavity filter ahead of the receiver, driven from a fanless mini-PC. This site replaced an older installation a few streets away which suits the unattended operating we do here.

## Recent operating history

The station logged around 721 observations last month and nothing about that changes for the catch-up.

Our sister site 2766 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Job intake is manual-review with rejections reported straight back to the network.

The 22 degree elevation floor this site used to run was lifted in June once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

For this shift only, we ask schedulers to respect a 38 degree minimum peak elevation; a tree line blocks most of the horizon. Outside that the site is open as normal. For the catch-up effort, between 2345Z on the 22nd and 0745Z on the 23rd the antenna is committed to other work; the rotator gearbox is being replaced. No other limits apply here. Ahead of the 22-25 July window, we are able to run 1 catch-up observations at most; the operator reviews each one by hand and cannot keep up beyond that. Normal service continues alongside.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over USB serial which is adequate for the passes we take.

## Software and configuration

The site runs satnogs-client 1.9 pinned to a known-good release which has avoided the regressions others hit.

## Neighbouring coverage

The regional group meets monthly to divide the load and duplicate scheduling is rare as a result.

## Typical traffic

We see mainly 2m and 70cm amateur payloads with the rest spread across other bands.

## Staffing

The station is run by 3 volunteers and handover notes are kept on the club wiki.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 2 kW inverter and the generator has never actually been needed. Data leaves the site over a 4G modem though the monthly allowance is not generous.

## Local interference

The local noise floor sits worst toward the north which mostly affects the weaker downlinks.

## Calibration

Rotator alignment was re-surveyed in May though we plan another check before winter.

## Fault handling

Alerts route to the site owner first, then the club with a monthly summary to the network.

## Data quality

Baseline noise sits about 3 dB above the network median so the occasional pass gets clipped. The host reboots for updates at 0400Z so treat marginal passes with a little caution.

## Other remarks

The Friday-morning routine maintenance we once ran between 0400Z and 1300Z ended in March and no longer applies.

## Contact

Contact details for station 2743 are on its network page and we usually reply within a day.
