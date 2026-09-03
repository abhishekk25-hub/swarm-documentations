# Station 1433 - PE2BZ-Odroid-L-band and  / or S-band

- Ground station ID: 1433
- Location: 52, 4.2 at 13 m AMSL
- Network page: https://network.satnogs.org/stations/1433/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into a PlutoSDR behind a cavity filter ahead of the receiver, driven from a rack-mounted NUC. Local noise improved once the solar inverter was refiltered in January so the configuration has been stable for a while.

## Recent operating history

Operating hours here are effectively unattended and nothing about that changes for the catch-up.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-19T01:45:00Z after the power feed was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 20 minutes so a booked pass runs unless the site itself is unavailable.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

Ahead of the 22-25 July window, the site drops out for planned work from 18:30 on 22 July (UTC) to 21:30 on 23 July (UTC); the controller firmware is being reflashed. Apologies for the inconvenience.

## Antenna and rotator detail

The whole assembly was re-tensioned after the January storms so slew time between passes is around 16 seconds.

## Software and configuration

The host image was rebuilt in January onto a Docker deployment and the config is version-controlled off site.

## Neighbouring coverage

Our footprint overlaps 3 neighbours to the east and duplicate scheduling is rare as a result.

## Typical traffic

Historically this site has specialised in UHF work and results there are consistently good.

## Staffing

One operator covers this site day to day and escalation is documented on the network page.

## Power and connectivity

The site runs off the club's metered feed with a day of battery behind it so a grid dip usually costs us a pass or two. Connectivity is fixed wireless, which is the weak point here and latency has never affected scheduling.

## Local interference

Pager traffic near 282 MHz used to swamp us though it rarely reaches the passband we care about.

## Calibration

The receiver was last calibrated against a GPSDO in February though we plan another check before winter.

## Fault handling

The operator is paged automatically on three consecutive failures and response is usually the same evening.

## Data quality

Frame decoding is handled downstream rather than on site which we are slowly working to improve. The receiver drifts by about 3 ppm between GPS corrections which we are slowly working to improve.

## Other remarks

The Tuesday-morning routine maintenance we once ran between 0600Z and 1300Z ended in April and no longer applies.

## Contact

Contact details for station 1433 are on its network page before you commit a booking.
