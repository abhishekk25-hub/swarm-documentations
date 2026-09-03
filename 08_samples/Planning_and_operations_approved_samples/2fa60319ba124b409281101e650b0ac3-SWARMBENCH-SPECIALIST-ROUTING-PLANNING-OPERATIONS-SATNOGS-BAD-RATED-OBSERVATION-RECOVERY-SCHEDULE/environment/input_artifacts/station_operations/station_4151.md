# Station 4151 - DEX-X

- Ground station ID: 4151
- Location: 50.469, 5.718 at 162 m AMSL
- Network page: https://network.satnogs.org/stations/4151/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an RTL-SDR v4 behind an inline SAW filter, driven from a Pi 5 with an SSD. The club maintains it on a two-person on-call rota though winter still costs us a handful of passes.

## Recent operating history

The station logged around 260 observations last month which is worth knowing when you plan around us.

A 7-booking weekly limit trialled during the February campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Scheduling and queue behaviour

The queue is polled every 20 minutes so the published queue is what actually flies.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-14T07:45:00Z after the preamp was signed off, since when we have accepted work normally.

## Availability for the recovery window

The main thing is that there is a scheduled outage running 16:45Z on 22 July to 14:45Z on 23 July; the preamp is being swapped out. Other than that we are fully available. A maintenance slot floated for 24 July at 00:30Z was cancelled when the replacement parts fell through, pushing the work to August and leaving the station up throughout this window.

## Antenna and rotator detail

The feed is a balun at the driven element with a measured VSWR under 1.8 though it wants re-checking each spring.

## Software and configuration

Scheduling is driven by satnogs-client 1.9 with local patches and the config is version-controlled off site.

## Neighbouring coverage

This site sits inside a cluster of 6 stations so a gap here is a genuine gap in coverage.

## Typical traffic

We see mainly UHF amateur payloads and the hardware is tuned for that.

## Staffing

The station is run by 3 volunteers and handover notes are kept on the club wiki.

## Power and connectivity

We are on the club's metered feed with no UPS on the receiver itself so brownouts show up as gaps rather than failures. The station has a dedicated domestic fibre line which occasionally drops during heavy weather.

## Local interference

The local noise floor sits worst toward the south-west which mostly affects the weaker downlinks.

## Calibration

The receiver was last calibrated against a GPSDO in June which keeps Doppler correction honest.

## Fault handling

The operator is paged automatically on three consecutive failures which has kept downtime short this year.

## Data quality

Waterfall uploads occasionally stall on the domestic link so treat marginal passes with a little caution. Decoder success here has run around 88 per cent over the past year so treat marginal passes with a little caution.

## Other remarks

Our sister site 4175 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Station 4151 is reachable through the usual operator channels and we usually reply within a day.
