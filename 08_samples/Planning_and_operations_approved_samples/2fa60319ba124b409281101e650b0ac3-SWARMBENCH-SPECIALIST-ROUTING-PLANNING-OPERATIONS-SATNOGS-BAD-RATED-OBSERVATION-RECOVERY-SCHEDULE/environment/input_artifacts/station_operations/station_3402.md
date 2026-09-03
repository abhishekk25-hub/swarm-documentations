# Station 3402 - StreetDirt S-Band

- Ground station ID: 3402
- Location: 52.2179, 5.1645 at 14 m AMSL
- Network page: https://network.satnogs.org/stations/3402/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a modified Wimo X-Quad into an SDRplay RSPdx behind a filtered preamp, driven from a Pi 5 with an SSD. Uptime last quarter ran at about 88 per cent and it has needed very little attention since.

## Recent operating history

We have been catching up on a backlog of our own since January though we do review anything anomalous.

An unplanned outage from 2026-06-13T02:00:00Z to 2026-06-13T16:00:00Z took the site down when the rotator controller failed, closed out at the time and with no bearing on the current recovery window.

## Scheduling and queue behaviour

The queue is polled every 5 minutes and duplicate submissions are dropped automatically.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Availability for the recovery window

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T16:45:00Z after the power feed was signed off, since when we have accepted work normally. Heads up -- the site can carry 1 make-good bookings in total; power budget at the site is tight. We will flag it if anything shifts.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 31 degrees though it wants re-checking each spring.

## Software and configuration

We track the upstream client but hold back one minor version so behaviour is predictable between updates.

## Neighbouring coverage

The nearest other station is roughly 354 km away so handing work over is usually straightforward.

## Typical traffic

Most of our traffic is 2m and 70cm weather and cubesat work which shapes how the antenna was built.

## Staffing

The site is unattended and checked remotely and escalation is documented on the network page.

## Power and connectivity

We are on the club's metered feed with no UPS on the receiver itself so a grid dip usually costs us a pass or two. Uplink is fixed wireless shared with the household so large waterfall uploads queue up overnight.

## Local interference

A 220 MHz carrier appears most weekday afternoons so we schedule around it where we can.

## Calibration

The chain was swept end to end in March though we plan another check before winter.

## Fault handling

Alerts route to the site owner first, then the club so problems rarely go unnoticed for long.

## Data quality

Frame decoding is handled downstream rather than on site so the occasional pass gets clipped. Waterfall uploads occasionally stall on the domestic link and downstream products are unaffected.

## Other remarks

A 8-booking weekly limit trialled during the May campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Reach the operator of station 3402 on the community forum if anything here needs clarifying.
