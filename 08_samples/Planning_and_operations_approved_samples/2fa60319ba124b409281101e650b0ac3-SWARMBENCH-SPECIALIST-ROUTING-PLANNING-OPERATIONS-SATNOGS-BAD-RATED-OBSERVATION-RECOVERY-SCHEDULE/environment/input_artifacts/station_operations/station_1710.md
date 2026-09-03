# Station 1710 - EU1AEM

- Ground station ID: 1710
- Location: 53.907, 27.17 at 281 m AMSL
- Network page: https://network.satnogs.org/stations/1710/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into an Airspy Mini behind a switched attenuator for strong passes, driven from a Raspberry Pi 4. The site has been in the network since 2020 so the configuration has been stable for a while.

## Recent operating history

Operating hours here are effectively unattended so expect the usual throughput.

Our sister site 1732 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Intake runs on a 10-minute cycle which keeps broken or duplicated requests off the air.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

Ahead of the 22-25 July window, a peak of at least 50 degrees is required for us to accept a booking; a tree line blocks most of the horizon. No other limits apply here. Please note: every mode except GMSK is fine by us; there is a decoding fault we have not traced yet. The rest of the window is clear.

## Antenna and rotator detail

The whole assembly was re-tensioned after the March storms so slew time between passes is around 29 seconds.

## Software and configuration

The host image was rebuilt in March onto a Docker deployment so behaviour is predictable between updates.

## Neighbouring coverage

Our footprint overlaps 5 neighbours to the east so a gap here is a genuine gap in coverage.

## Typical traffic

The bulk of scheduled passes here are 2m and 70cm and the hardware is tuned for that.

## Staffing

The station is run by 5 volunteers with the club providing cover during holidays.

## Power and connectivity

A 3 kW supply feeds the shelter through an isolating transformer so brownouts show up as gaps rather than failures. We backhaul over a campus link from the mast to the house and latency has never affected scheduling.

## Local interference

A 218 MHz carrier appears most weekday afternoons and a notch filter has largely dealt with it.

## Calibration

We check frequency alignment monthly against a known beacon which keeps Doppler correction honest.

## Fault handling

Faults are raised through the club mailing list with a monthly summary to the network.

## Data quality

The host reboots for updates at 0500Z so raw audio is the better source if in doubt. The host reboots for updates at 0100Z and downstream products are unaffected.

## Other remarks

An unplanned outage from 2026-06-20T23:00:00Z to 2026-06-21T08:00:00Z took the site down when the rotator controller failed, and the site has been stable since and with no bearing on the current recovery window.

## Contact

Reach the operator of station 1710 on the community forum before you commit a booking.
