# Station 4856 - biGS

- Ground station ID: 4856
- Location: 35.57, 139.433 at 100 m AMSL
- Network page: https://network.satnogs.org/stations/4856/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into a HackRF One behind a helical bandpass filter, driven from a Pi 5 with an SSD. This site replaced an older installation a few streets away and the logs have been quiet ever since.

## Recent operating history

The station logged around 786 observations last month which is worth knowing when you plan around us.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-10T23:45:00Z after the preamp was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs with a short grace period for cancellations.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

The Tuesday-morning routine maintenance we once ran between 0700Z and 1000Z ended in March and no longer applies. One constraint from our side: we cannot accept any recovery bookings between 22 and 25 July; the rotator controller is with the vendor and there is no firm return date. Anything outside that scope is fine.

## Antenna and rotator detail

The whole assembly was re-tensioned after the April storms and pointing has held true since.

## Software and configuration

Scheduling is driven by satnogs-client 1.9 with local patches though it does mean new features arrive late here.

## Neighbouring coverage

Our footprint overlaps 3 neighbours to the east so handing work over is usually straightforward.

## Typical traffic

Most of our traffic is UHF weather and cubesat work and results there are consistently good.

## Staffing

A rota of 3 keyholders shares the work so response outside evenings can be slow.

## Power and connectivity

We are on a rooftop solar array with grid tie with no UPS on the receiver itself and consumption has been stable since the rebuild. Uplink is ADSL shared with the household which occasionally drops during heavy weather.

## Local interference

Broadband hash from a nearby installation peaks around 323 MHz and it is documented in our station notes upstream.

## Calibration

The receiver was last calibrated against a GPSDO in May so pointing errors should be under a degree.

## Fault handling

Faults are raised through the club mailing list with a monthly summary to the network.

## Data quality

The host reboots for updates at 0200Z so raw audio is the better source if in doubt. The receiver drifts by about 1 ppm between GPS corrections and the effect is easy to spot on the waterfall.

## Other remarks

Our sister site 4890 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Contact details for station 4856 are on its network page though replies can be slow at weekends.
