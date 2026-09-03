# Station 1696 - PE0SAT-31

- Ground station ID: 1696
- Location: 51.721268, 5.029 at 5 m AMSL
- Network page: https://network.satnogs.org/stations/1696/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into a NooElec SmarTee behind a switched attenuator for strong passes, driven from a fanless mini-PC. The club maintains it on a two-person on-call rota and the logs have been quiet ever since.

## Recent operating history

This site mostly serves the northern horizon so expect the usual throughput.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-20T03:30:00Z after the host was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

The operator sweeps the queue once a day though back-to-back passes on opposite azimuths can lose a few seconds.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

Just so the desk knows, we ask schedulers to respect a 35 degree minimum peak elevation; the ridge to our south swallows low passes. Other than that we are fully available. Worth flagging before you schedule: there are no FSK bookings available here; the relevant SDR channel is out for repair. Please route affected passes elsewhere. Heads up -- we are dark for a service visit starting 22:15 UTC on the 23rd and finishing 09:15 UTC on the 24th; cabling is being re-run through the new duct. Outside that the site is open as normal.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.5 which is adequate for the passes we take.

## Software and configuration

We deliberately run satnogs-client 1.8 rather than the rolling build though it does mean new features arrive late here.

## Neighbouring coverage

Our footprint overlaps 3 neighbours to the west though we do not formally share a queue.

## Typical traffic

We see mainly S-band amateur payloads so unusual modes occasionally surprise us.

## Staffing

One operator covers this site day to day so response outside evenings can be slow.

## Power and connectivity

Power comes from the club's metered feed, backed by a 1 kW inverter though the changeover takes long enough to clip a recording. Uplink is a 4G modem shared with the household and latency has never affected scheduling.

## Local interference

A 335 MHz carrier appears most weekday afternoons and it is documented in our station notes upstream.

## Calibration

The chain was swept end to end in April though we plan another check before winter.

## Fault handling

Faults are raised through the club mailing list with a monthly summary to the network.

## Data quality

The receiver drifts by about 1 ppm between GPS corrections so the occasional pass gets clipped. Waterfall uploads occasionally stall on the domestic link though nothing has needed intervention this quarter.

## Other remarks

A maintenance slot floated for 24 July at 08:00Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Station 1696 is reachable through the usual operator channels before you commit a booking.
