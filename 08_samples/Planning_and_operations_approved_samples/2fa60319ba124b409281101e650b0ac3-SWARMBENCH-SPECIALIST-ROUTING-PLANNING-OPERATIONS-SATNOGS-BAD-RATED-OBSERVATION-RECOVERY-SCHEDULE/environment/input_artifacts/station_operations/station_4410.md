# Station 4410 - Prodromos

- Ground station ID: 4410
- Location: 40.1389788, -105.1509764 at 1524 m AMSL
- Network page: https://network.satnogs.org/stations/4410/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into a HackRF One behind an inline SAW filter, driven from a Raspberry Pi 4. This site replaced an older installation a few streets away so the configuration has been stable for a while.

## Recent operating history

Volunteers rebuilt the feed arrangement in January so expect the usual throughput.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-09T22:45:00Z after the host was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

The operator sweeps the queue once a day and nothing already on air is ever pre-empted.

Our sister site 4435 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

We are fully operational for the catch-up period with no local limits. Normal scheduling rules apply.

## Antenna and rotator detail

The feed is a hairpin match with a measured VSWR under 1.8 though it wants re-checking each spring.

## Software and configuration

Scheduling is driven by satnogs-client 1.9 with local patches and the config is version-controlled off site.

## Neighbouring coverage

We coordinate informally with 6 nearby sites so handing work over is usually straightforward.

## Typical traffic

Most of our traffic is UHF weather and cubesat work and the hardware is tuned for that.

## Staffing

Day-to-day operation is fully automated which keeps the workload manageable.

## Power and connectivity

Power comes from the building's landlord supply, backed by a 2 kW inverter though the changeover takes long enough to clip a recording. We backhaul over a 4G modem from the mast to the house so large waterfall uploads queue up overnight.

## Local interference

Pager traffic near 230 MHz used to swamp us which the operator re-checks each quarter.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source which keeps Doppler correction honest.

## Fault handling

Escalation goes to whichever keyholder is on the rota with a monthly summary to the network.

## Data quality

Baseline noise sits about 1 dB above the network median and downstream products are unaffected. Frame decoding is handled downstream rather than on site which rarely defeats the decoder outright.

## Other remarks

A maintenance slot floated for 24 July at 21:30Z was cancelled when the replacement parts fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Contact details for station 4410 are on its network page and we are happy to discuss alternatives.
