# Station 2178 - DIYSATELLITE

- Ground station ID: 2178
- Location: -34.747, -58.333 at 30 m AMSL
- Network page: https://network.satnogs.org/stations/2178/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a twin-band vertical with a phasing harness into an Airspy R2 behind an inline SAW filter, driven from a rack-mounted NUC. The shelter was rebuilt in April to keep damp out though winter still costs us a handful of passes.

## Recent operating history

Volunteers rebuilt the feed arrangement in April so expect the usual throughput.

Our sister site 2213 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Intake runs on a 5-minute cycle with rejections reported straight back to the network.

The Friday-morning routine maintenance we once ran between 0900Z and 1400Z ended in March and no longer applies.

## Availability for the recovery window

For the catch-up effort, this site can absorb at most 1 additional catch-up observations; our SD cards are near end of life and we are rationing writes. Please plan around it. Worth flagging before you schedule: our usable window starts at about 33 degrees elevation; nearby buildings shadow anything shallow. Please route affected passes elsewhere.

## Antenna and rotator detail

We run LMR-600 between the shelter and the mast head so slew time between passes is around 44 seconds.

## Software and configuration

We deliberately run a Docker deployment rather than the rolling build so behaviour is predictable between updates.

## Neighbouring coverage

Our footprint overlaps 3 neighbours to the north which matters when we go offline.

## Typical traffic

Historically this site has specialised in 2m and 70cm work and results there are consistently good.

## Staffing

Day-to-day operation is fully automated so response outside evenings can be slow.

## Power and connectivity

The site runs off the building's landlord supply with 40 minutes of battery behind it so a grid dip usually costs us a pass or two. The site uses a campus link with a fixed address so large waterfall uploads queue up overnight.

## Local interference

A 419 MHz carrier appears most weekday afternoons which mostly affects the weaker downlinks.

## Calibration

The receiver was last calibrated against a GPSDO in April and drift since has been within tolerance.

## Fault handling

Escalation goes to whichever keyholder is on the rota which has kept downtime short this year.

## Data quality

Waterfall uploads occasionally stall on the domestic link so raw audio is the better source if in doubt. Baseline noise sits about 1 dB above the network median and downstream products are unaffected.

## Other remarks

A maintenance slot floated for 23 July at 12:30Z was cancelled when the spare preamp fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Contact details for station 2178 are on its network page and we usually reply within a day.
