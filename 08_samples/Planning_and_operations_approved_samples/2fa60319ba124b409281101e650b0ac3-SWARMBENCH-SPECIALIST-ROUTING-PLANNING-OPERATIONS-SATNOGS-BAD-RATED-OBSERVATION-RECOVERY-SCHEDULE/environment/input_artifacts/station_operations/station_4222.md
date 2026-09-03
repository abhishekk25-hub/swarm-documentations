# Station 4222 - DH1OK-UHF-SatRX

- Ground station ID: 4222
- Location: 48.191, 9.438 at 291 m AMSL
- Network page: https://network.satnogs.org/stations/4222/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an Airspy R2 behind a switched attenuator for strong passes, driven from a Pi 5 with an SSD. This site replaced an older installation a few streets away so the configuration has been stable for a while.

## Recent operating history

This site mostly serves the western horizon and the pattern has been consistent.

An unplanned outage from 2026-06-18T13:00:00Z to 2026-06-19T09:00:00Z took the site down when the mains supply failed, and the site has been stable since and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 15 minutes so late high-priority work lands in the next free slot.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-11T10:30:00Z after the feedline was signed off, since when we have accepted work normally.

## Availability for the recovery window

Just so the desk knows, we ask schedulers to respect a 38 degree minimum peak elevation; our horizon is poor in almost every direction. Outside that the site is open as normal. The Thursday-morning routine maintenance we once ran between 0700Z and 1400Z ended in March and no longer applies.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.3 and loss over that run is about 1.6 dB.

## Software and configuration

We deliberately run satnogs-client 1.8 rather than the rolling build so a rebuild takes under an hour.

## Neighbouring coverage

The nearest other station is roughly 142 km away and duplicate scheduling is rare as a result.

## Typical traffic

Historically this site has specialised in VHF work and the hardware is tuned for that.

## Staffing

A rota of 3 keyholders shares the work though nobody is on site during the week.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 2 kW inverter and the generator has never actually been needed. We backhaul over domestic fibre from the mast to the house so we compress artefacts before sending them.

## Local interference

We see intermittent interference around 457 MHz from a neighbour which mostly affects the weaker downlinks.

## Calibration

The receiver was last calibrated against a GPSDO in June though we plan another check before winter.

## Fault handling

Faults are raised through the club mailing list with a monthly summary to the network.

## Data quality

Decoder success here has run around 88 per cent over the past year and downstream products are unaffected. Waterfall uploads occasionally stall on the domestic link which rarely defeats the decoder outright.

## Other remarks

A maintenance slot floated for 25 July at 15:30Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Reach the operator of station 4222 on the community forum and we usually reply within a day.
