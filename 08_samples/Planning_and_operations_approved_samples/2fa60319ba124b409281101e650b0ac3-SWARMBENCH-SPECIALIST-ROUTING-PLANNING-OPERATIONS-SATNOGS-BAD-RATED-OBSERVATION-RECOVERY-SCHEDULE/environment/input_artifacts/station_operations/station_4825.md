# Station 4825 - PISTATION-VHF

- Ground station ID: 4825
- Location: 49.23156330169167, -121.75928951127115 at 20 m AMSL
- Network page: https://network.satnogs.org/stations/4825/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into an Airspy Mini behind a bias-tee LNA at the mast head, driven from an Odroid in the loft. The mast was re-aligned in March after a storm though winter still costs us a handful of passes.

## Recent operating history

Traffic through this site has been steady all summer though we do review anything anomalous.

The Friday-morning routine maintenance we once ran between 0800Z and 1200Z ended in May and no longer applies.

## Scheduling and queue behaviour

The queue is polled every 10 minutes though the overnight window is checked only once.

A 7-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

Before anything is booked, our FSK chain is out of service, so do not book it; sample rates for it exceed what the host can sustain. Anything outside that scope is fine. Expect nothing usable from 15:45 on 22 July (UTC) right through to 05:45 on 23 July (UTC); the preamp is being swapped out. Nothing else about the site changes.

## Antenna and rotator detail

Azimuth travel is limited to 340 degrees by the mast stay which suits our mostly-overhead traffic.

## Software and configuration

Automation here is the stock Raspbian image plus a handful of cron jobs so a rebuild takes under an hour.

## Neighbouring coverage

The regional group meets monthly to divide the load so handing work over is usually straightforward.

## Typical traffic

We see mainly S-band amateur payloads with the rest spread across other bands.

## Staffing

The station is run by 2 volunteers so response outside evenings can be slow.

## Power and connectivity

The rack draws about 62 W continuous from a rooftop solar array with grid tie which has ridden out every cut so far this year. The site uses a campus link with a fixed address and latency has never affected scheduling.

## Local interference

A survey in February found a persistent birdie near 287 MHz which mostly affects the weaker downlinks.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source and drift since has been within tolerance.

## Fault handling

Escalation goes to whichever keyholder is on the rota and the log is public on request.

## Data quality

The host reboots for updates at 0400Z so the occasional pass gets clipped. Frame decoding is handled downstream rather than on site so treat marginal passes with a little caution.

## Other remarks

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Contact

Scheduling questions go to the owner through the station 4825 profile page and we usually reply within a day.
