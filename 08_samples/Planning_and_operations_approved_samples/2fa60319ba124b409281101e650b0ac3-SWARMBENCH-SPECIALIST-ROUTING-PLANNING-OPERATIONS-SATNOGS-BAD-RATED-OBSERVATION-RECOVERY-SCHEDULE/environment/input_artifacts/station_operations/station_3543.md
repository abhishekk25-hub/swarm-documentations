# Station 3543 - StreetDirt S-band parabolic

- Ground station ID: 3543
- Location: 52.2179, 5.1645 at 14 m AMSL
- Network page: https://network.satnogs.org/stations/3543/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into a NooElec SmarTee behind a bias-tee LNA at the mast head, driven from an Odroid in the loft. This site replaced an older installation a few streets away and the owner checks it over most weekends.

## Recent operating history

This site mostly serves the southern horizon which is worth knowing when you plan around us.

The Wednesday-morning routine maintenance we once ran between 0600Z and 1400Z ended in May and no longer applies.

## Scheduling and queue behaviour

Scheduling here is fully automated so a booked pass runs unless the site itself is unavailable.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T06:30:00Z after the rotator was signed off, since when we have accepted work normally.

## Availability for the recovery window

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T06:30:00Z after the rotator was signed off, since when we have accepted work normally. In short, our ceiling for this exercise is 1 bookings; storage fills faster than we can offload. We will flag it if anything shifts. For the avoidance of doubt, we lose the station to engineering between 19:15 UTC on the 23rd and 17:15 UTC on the 24th; cabling is being re-run through the new duct. We can take anything else you send us.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 30 degrees though it wants re-checking each spring.

## Software and configuration

Automation here is a Docker deployment plus a handful of cron jobs though it does mean new features arrive late here.

## Neighbouring coverage

The regional group meets monthly to divide the load which matters when we go offline.

## Typical traffic

Most of our traffic is S-band weather and cubesat work with the rest spread across other bands.

## Staffing

The station is run by 3 volunteers with the club providing cover during holidays.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 5 kW inverter and the generator has never actually been needed. We backhaul over domestic fibre from the mast to the house and latency has never affected scheduling.

## Local interference

A 158 MHz carrier appears most weekday afternoons which the operator re-checks each quarter.

## Calibration

We check frequency alignment monthly against a known beacon and nothing has moved since.

## Fault handling

Faults are raised through the club mailing list with a monthly summary to the network.

## Data quality

The host reboots for updates at 0300Z which rarely defeats the decoder outright. Frame decoding is handled downstream rather than on site so treat marginal passes with a little caution.

## Other remarks

The 22 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Contact

Station 3543 is reachable through the usual operator channels though replies can be slow at weekends.
