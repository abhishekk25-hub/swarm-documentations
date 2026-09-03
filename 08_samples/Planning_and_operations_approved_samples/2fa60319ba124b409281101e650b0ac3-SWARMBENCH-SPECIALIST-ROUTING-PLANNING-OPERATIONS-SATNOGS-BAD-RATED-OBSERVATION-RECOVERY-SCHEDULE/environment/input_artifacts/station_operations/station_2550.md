# Station 2550 - USU GAS Yagi Az+El

- Ground station ID: 2550
- Location: 41.743, -111.807 at 1382 m AMSL
- Network page: https://network.satnogs.org/stations/2550/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into a PlutoSDR behind a cavity filter ahead of the receiver, driven from a Pi 5 with an SSD. Local noise improved once the heat pump was refiltered in June which is about what we expect for this hardware.

## Recent operating history

Traffic through this site has been steady all summer and the pattern has been consistent.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-11T20:15:00Z after the preamp was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

We cap pending work at roughly 30 jobs so a booked pass runs unless the site itself is unavailable.

Our sister site 2569 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

To save you a wasted slot, no FSK AX.100 Mode 5 please, though anything else is welcome; we have no working decoder for it at present. We will flag it if anything shifts. A maintenance slot floated for 25 July at 05:00Z was cancelled when the replacement parts fell through, pushing the work to September and leaving the station up throughout this window. While the catch-up runs, we hold a 48 degree floor on maximum elevation for booked work; the site sits in a bowl with high ground all round. The rest of the window is clear. For planning purposes, we will take 1 and decline anything beyond that; storage fills faster than we can offload. Normal service continues alongside.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over GPIO from the host and pointing has held true since.

## Software and configuration

Scheduling is driven by a Docker deployment with local patches though it does mean new features arrive late here.

## Neighbouring coverage

The nearest other station is roughly 72 km away so a gap here is a genuine gap in coverage.

## Typical traffic

The bulk of scheduled passes here are 2m and 70cm though we take whatever the network sends.

## Staffing

A rota of 3 keyholders shares the work so response outside evenings can be slow.

## Power and connectivity

Power comes from a domestic single-phase supply, backed by a 2 kW inverter so a grid dip usually costs us a pass or two. Uplink is ADSL shared with the household which occasionally drops during heavy weather.

## Local interference

The local noise floor sits worst toward the north and it is documented in our station notes upstream.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source though we plan another check before winter.

## Fault handling

Faults are raised through the club mailing list with a monthly summary to the network.

## Data quality

Waterfall uploads occasionally stall on the domestic link so raw audio is the better source if in doubt. Baseline noise sits about 1 dB above the network median which rarely defeats the decoder outright.

## Other remarks

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Contact

Scheduling questions go to the owner through the station 2550 profile page and we are happy to discuss alternatives.
