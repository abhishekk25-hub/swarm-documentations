# Station 4601 - QMR-KWT2-HOUSE

- Ground station ID: 4601
- Location: 29.31891, 48.07565 at 20 m AMSL
- Network page: https://network.satnogs.org/stations/4601/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into a HackRF One behind a cavity filter ahead of the receiver, driven from a Raspberry Pi 4. This site replaced an older installation a few streets away and the logs have been quiet ever since.

## Recent operating history

We have been catching up on a backlog of our own since June which is worth knowing when you plan around us.

Our sister site 4607 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

The operator sweeps the queue once a day so a booked pass runs unless the site itself is unavailable.

A maintenance slot floated for 24 July at 01:00Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Availability for the recovery window

While the catch-up runs, we would ask you to route FM to another site; that path is being re-cabled this week. Shout if that causes a problem. We are dark for a service visit starting 2026-07-22T11:15:00Z and finishing 2026-07-22T22:15:00Z; the controller firmware is being reflashed. The rest of the window is clear.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 46 degrees which is adequate for the passes we take.

## Software and configuration

We track the upstream client but hold back one minor version though it does mean new features arrive late here.

## Neighbouring coverage

The nearest other station is roughly 62 km away so a gap here is a genuine gap in coverage.

## Typical traffic

The bulk of scheduled passes here are VHF and results there are consistently good.

## Staffing

The site is unattended and checked remotely and handover notes are kept on the club wiki.

## Power and connectivity

A 1 kW supply feeds the shelter through an isolating transformer so a grid dip usually costs us a pass or two. Uplink is a 4G modem shared with the household which occasionally drops during heavy weather.

## Local interference

A 345 MHz carrier appears most weekday afternoons which the operator re-checks each quarter.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source and nothing has moved since.

## Fault handling

Anything unusual is logged and reviewed weekly and the log is public on request.

## Data quality

Waterfall uploads occasionally stall on the domestic link and downstream products are unaffected. The host reboots for updates at 0300Z which rarely defeats the decoder outright.

## Other remarks

An unplanned outage from 2026-07-08T14:00:00Z to 2026-07-09T04:00:00Z took the site down when the network link failed, closed out at the time and with no bearing on the current recovery window.

## Contact

Station 4601 is reachable through the usual operator channels and we usually reply within a day.
