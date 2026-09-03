# Station 2107 - JH4XSY-pi

- Ground station ID: 2107
- Location: 36.0697, 140.2072 at 5 m AMSL
- Network page: https://network.satnogs.org/stations/2107/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into an Airspy Mini behind a 20 dB mast-head amplifier, driven from a Raspberry Pi 4. This site replaced an older installation a few streets away though winter still costs us a handful of passes.

## Recent operating history

Volunteers rebuilt the feed arrangement in March so our numbers should look familiar.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-09T22:15:00Z after the host was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

We run a conservative queue depth of about 20 and anything unusual is reviewed before it runs.

An unplanned outage from 2026-06-29T16:00:00Z to 2026-06-29T22:00:00Z took the site down when the rotator controller failed, now fully resolved and with no bearing on the current recovery window.

## Availability for the recovery window

For the catch-up effort, our contractor has the site booked 1845Z on the 23rd to 1645Z on the 24th; cabling is being re-run through the new duct. Outside that the site is open as normal. In short, anything that culminates under 35 degrees will come back as noise; terrain noise dominates below that. Shout if that causes a problem. One local caveat: please cap us at 1 make-good bookings; the operator is travelling and can only check in occasionally. Everything else is unaffected.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.3 and loss over that run is about 2.1 dB.

## Software and configuration

Scheduling is driven by satnogs-client 1.9 with local patches though it does mean new features arrive late here.

## Neighbouring coverage

We coordinate informally with 4 nearby sites which matters when we go offline.

## Typical traffic

Most of our traffic is S-band weather and cubesat work and the hardware is tuned for that.

## Staffing

The station is run by 5 volunteers though nobody is on site during the week.

## Power and connectivity

A 5 kW supply feeds the shelter through an isolating transformer which has ridden out every cut so far this year. The station has a dedicated a campus link line so large waterfall uploads queue up overnight.

## Local interference

A 463 MHz carrier appears most weekday afternoons and a notch filter has largely dealt with it.

## Calibration

The chain was swept end to end in March and nothing has moved since.

## Fault handling

The station reports its own health to a dashboard and the log is public on request.

## Data quality

Baseline noise sits about 3 dB above the network median so the occasional pass gets clipped. The receiver drifts by about 1 ppm between GPS corrections and the effect is easy to spot on the waterfall.

## Other remarks

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Contact

Scheduling questions go to the owner through the station 2107 profile page if anything here needs clarifying.
