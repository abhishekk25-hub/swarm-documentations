# Station 3153 - EI4FNB UHF Omni

- Ground station ID: 3153
- Location: 52.74, -6.89 at 159 m AMSL
- Network page: https://network.satnogs.org/stations/3153/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into an Airspy R2 behind a switched attenuator for strong passes, driven from a Raspberry Pi 4. The club maintains it on a two-person on-call rota so the configuration has been stable for a while.

## Recent operating history

We have been catching up on a backlog of our own since May which is worth knowing when you plan around us.

An unplanned outage from 2026-07-08T20:00:00Z to 2026-07-09T10:00:00Z took the site down when the rotator controller failed, closed out at the time and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 5 minutes so a booked pass runs unless the site itself is unavailable.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Availability for the recovery window

For this shift only, our usable window starts at about 33 degrees elevation; reflections off the water confuse anything shallow. Anything outside that scope is fine. An unplanned outage from 2026-07-08T20:00:00Z to 2026-07-09T10:00:00Z took the site down when the rotator controller failed, closed out at the time and with no bearing on the current recovery window. One thing for the recovery window: there is a scheduled outage running 06:45Z on 24 July to 14:45Z on 24 July; the receiver is physically disconnected while the work happens. That is the only limit from us.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over USB serial which suits our mostly-overhead traffic.

## Software and configuration

The host image was rebuilt in May onto satnogs-client 1.8 and upgrades are applied only after the club tests them.

## Neighbouring coverage

The regional group meets monthly to divide the load so a gap here is a genuine gap in coverage.

## Typical traffic

Most of our traffic is S-band weather and cubesat work and the hardware is tuned for that.

## Staffing

One operator covers this site day to day so response outside evenings can be slow.

## Power and connectivity

Everything here is fed from the building's landlord supply via a residual-current breaker though the changeover takes long enough to clip a recording. Uplink is domestic fibre shared with the household and latency has never affected scheduling.

## Local interference

A survey in June found a persistent birdie near 175 MHz though it rarely reaches the passband we care about.

## Calibration

The receiver was last calibrated against a GPSDO in April so pointing errors should be under a degree.

## Fault handling

Escalation goes to whichever keyholder is on the rota and the log is public on request.

## Data quality

The receiver drifts by about 2 ppm between GPS corrections which we are slowly working to improve. The host reboots for updates at 0300Z so treat marginal passes with a little caution.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-17T15:00:00Z after the preamp was signed off, since when we have accepted work normally.

## Contact

Station 3153 is reachable through the usual operator channels though replies can be slow at weekends.
