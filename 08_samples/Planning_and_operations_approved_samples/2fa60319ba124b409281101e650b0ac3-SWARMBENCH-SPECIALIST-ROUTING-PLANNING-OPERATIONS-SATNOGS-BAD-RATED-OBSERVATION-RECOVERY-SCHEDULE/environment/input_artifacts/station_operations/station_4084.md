# Station 4084 - Astronomiemuseum Turnstile VHF (Test UHF)

- Ground station ID: 4084
- Location: 50.37722, 11.18972 at 640 m AMSL
- Network page: https://network.satnogs.org/stations/4084/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into a NooElec SmarTee behind a bias-tee LNA at the mast head, driven from a Pi 5 with an SSD. Weather exposure is the main limiting factor here so the configuration has been stable for a while.

## Recent operating history

We have been catching up on a backlog of our own since March which is worth knowing when you plan around us.

The 22 degree elevation floor this site used to run was lifted in February once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 10 minutes and nothing already on air is ever pre-empted.

The Tuesday-morning routine maintenance we once ran between 0800Z and 1400Z ended in March and no longer applies.

## Availability for the recovery window

Heads up -- our contractor has the site booked 1030Z on the 24th to 2130Z on the 24th; the controller firmware is being reflashed. Do factor that into the plan.

## Antenna and rotator detail

We run LMR-600 between the shelter and the mast head and loss over that run is about 1.6 dB.

## Software and configuration

The site runs a Docker deployment pinned to a known-good release though it does mean new features arrive late here.

## Neighbouring coverage

The nearest other station is roughly 133 km away so a gap here is a genuine gap in coverage.

## Typical traffic

Most of our traffic is S-band weather and cubesat work so unusual modes occasionally surprise us.

## Staffing

One operator covers this site day to day so response outside evenings can be slow.

## Power and connectivity

Everything here is fed from a rooftop solar array with grid tie via a residual-current breaker which has ridden out every cut so far this year. Data leaves the site over a 4G modem so large waterfall uploads queue up overnight.

## Local interference

Pager traffic near 210 MHz used to swamp us though it rarely reaches the passband we care about.

## Calibration

The chain was swept end to end in June with results filed on the station page.

## Fault handling

Alerts route to the site owner first, then the club so problems rarely go unnoticed for long.

## Data quality

Baseline noise sits about 2 dB above the network median and the effect is easy to spot on the waterfall. Frame decoding is handled downstream rather than on site which we are slowly working to improve.

## Other remarks

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Contact

Contact details for station 4084 are on its network page before you commit a booking.
