# Station 4326 - KB9LEB_Debian_12

- Ground station ID: 4326
- Location: 29.0241436, -80.9789164 at 26 m AMSL
- Network page: https://network.satnogs.org/stations/4326/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into an SDRplay RSPdx behind a 20 dB mast-head amplifier, driven from an old ThinkPad in the garage. The site has been in the network since 2021 which suits the unattended operating we do here.

## Recent operating history

Traffic through this site has been steady all summer though we do review anything anomalous.

The Thursday-morning routine maintenance we once ran between 0600Z and 1100Z ended in June and no longer applies.

## Scheduling and queue behaviour

The queue is polled every 15 minutes with a short grace period for cancellations.

A 5-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

BPSK is the one thing we cannot take this window; we have no working decoder for it at present. That is the only limit from us. A practical point: an engineer is on site from 2100Z on the 24th to 0000Z on the 26th and the chain will be broken; cabling is being re-run through the new duct. Do factor that into the plan. A maintenance slot floated for 23 July at 07:00Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Antenna and rotator detail

The whole assembly was re-tensioned after the June storms which is adequate for the passes we take.

## Software and configuration

The site runs the stock Raspbian image pinned to a known-good release though it does mean new features arrive late here.

## Neighbouring coverage

The regional group meets monthly to divide the load which matters when we go offline.

## Typical traffic

The bulk of scheduled passes here are S-band and results there are consistently good.

## Staffing

A rota of 4 keyholders shares the work so response outside evenings can be slow.

## Power and connectivity

Everything here is fed from a domestic single-phase supply via a residual-current breaker and the generator has never actually been needed. We backhaul over fixed wireless from the mast to the house so large waterfall uploads queue up overnight.

## Local interference

Pager traffic near 374 MHz used to swamp us so we schedule around it where we can.

## Calibration

Rotator alignment was re-surveyed in February so pointing errors should be under a degree.

## Fault handling

Alerts route to the site owner first, then the club which has kept downtime short this year.

## Data quality

Frame decoding is handled downstream rather than on site though nothing has needed intervention this quarter. The host reboots for updates at 0200Z and the effect is easy to spot on the waterfall.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-16T04:45:00Z after the preamp was signed off, since when we have accepted work normally.

## Contact

Reach the operator of station 4326 on the community forum and we are happy to discuss alternatives.
