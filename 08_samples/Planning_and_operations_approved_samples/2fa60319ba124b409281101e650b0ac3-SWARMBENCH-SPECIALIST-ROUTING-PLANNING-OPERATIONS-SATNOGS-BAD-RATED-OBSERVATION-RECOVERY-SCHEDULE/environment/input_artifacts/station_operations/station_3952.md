# Station 3952 - UT5U**

- Ground station ID: 3952
- Location: 50.436, 30.545 at 220 m AMSL
- Network page: https://network.satnogs.org/stations/3952/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into an RTL-SDR Blog v3 behind a 20 dB mast-head amplifier, driven from a Pi 5 with an SSD. Weather exposure is the main limiting factor here which suits the unattended operating we do here.

## Recent operating history

We have been catching up on a backlog of our own since March so our numbers should look familiar.

A 7-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Scheduling and queue behaviour

We cap pending work at roughly 30 jobs and nothing already on air is ever pre-empted.

The Wednesday-morning routine maintenance we once ran between 0600Z and 1100Z ended in March and no longer applies.

## Availability for the recovery window

An earlier revision of this note listed a booking freeze, lifted at 2026-07-18T18:15:00Z after the power feed was signed off, since when we have accepted work normally. The main thing is that anything peaking below 43 degrees is unusable here; a new building went up on the near skyline. Please plan around it. While the catch-up runs, FSK is the one thing we cannot take this window; it shares hardware with the beacon monitor, which is tied up. We remain open either side of it.

## Antenna and rotator detail

The rotator is a SPID RAS driven over USB serial so slew time between passes is around 84 seconds.

## Software and configuration

The site runs the stock Raspbian image pinned to a known-good release and the config is version-controlled off site.

## Neighbouring coverage

The regional group meets monthly to divide the load so a gap here is a genuine gap in coverage.

## Typical traffic

Most of our traffic is VHF weather and cubesat work and the hardware is tuned for that.

## Staffing

Two members handle maintenance between them with the club providing cover during holidays.

## Power and connectivity

A 3 kW supply feeds the shelter through an isolating transformer so a grid dip usually costs us a pass or two. The site uses a campus link with a fixed address and latency has never affected scheduling.

## Local interference

The local noise floor sits worst toward the south-west so we schedule around it where we can.

## Calibration

Rotator alignment was re-surveyed in March though we plan another check before winter.

## Fault handling

Faults are raised through the club mailing list which has kept downtime short this year.

## Data quality

Decoder success here has run around 96 per cent over the past year which rarely defeats the decoder outright. Frame decoding is handled downstream rather than on site and downstream products are unaffected.

## Other remarks

An unplanned outage from 2026-07-09T13:00:00Z to 2026-07-10T03:00:00Z took the site down when the network link failed, and the site has been stable since and with no bearing on the current recovery window.

## Contact

Scheduling questions go to the owner through the station 3952 profile page before you commit a booking.
