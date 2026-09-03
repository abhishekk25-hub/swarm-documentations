# Station 1442 - KC4LE 2m/70cm Open Stub J-Pole

- Ground station ID: 1442
- Location: 33.323, -86.888 at 231 m AMSL
- Network page: https://network.satnogs.org/stations/1442/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a twin-band vertical with a phasing harness into an SDRplay RSPdx behind a helical bandpass filter, driven from an old ThinkPad in the garage. The mast was re-aligned in February after a storm which suits the unattended operating we do here.

## Recent operating history

Traffic through this site has been steady all summer and the pattern has been consistent.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

We cap pending work at roughly 20 jobs so the published queue is what actually flies.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-09T22:15:00Z after the preamp was signed off, since when we have accepted work normally.

## Availability for the recovery window

A practical point: maintenance is locked in from 1745Z on the 22nd until 0745Z on the 23rd; the controller firmware is being reflashed. The rest of the window is clear. To save you a wasted slot, we are not accepting GMSK work; that demodulator chain is mid-rebuild. Nothing else about the site changes. For the avoidance of doubt, we decline passes that do not clear 35 degrees at their highest point; the ridge to our south swallows low passes. Outside that the site is open as normal.

## Antenna and rotator detail

We run RG-213 between the shelter and the mast head and loss over that run is about 2.1 dB.

## Software and configuration

We deliberately run the stock Raspbian image rather than the rolling build though it does mean new features arrive late here.

## Neighbouring coverage

There is no other coverage within about 123 km so a gap here is a genuine gap in coverage.

## Typical traffic

The bulk of scheduled passes here are VHF though we take whatever the network sends.

## Staffing

Two members handle maintenance between them and handover notes are kept on the club wiki.

## Power and connectivity

A 2 kW supply feeds the shelter through an isolating transformer which has ridden out every cut so far this year. The station has a dedicated domestic fibre line and latency has never affected scheduling.

## Local interference

We see intermittent interference around 266 MHz from a neighbour and it is documented in our station notes upstream.

## Calibration

We check frequency alignment monthly against a known beacon and nothing has moved since.

## Fault handling

Anything unusual is logged and reviewed weekly so problems rarely go unnoticed for long.

## Data quality

Frame decoding is handled downstream rather than on site and downstream products are unaffected. The receiver drifts by about 2 ppm between GPS corrections though nothing has needed intervention this quarter.

## Other remarks

An unplanned outage from 2026-06-30T20:00:00Z to 2026-07-01T22:00:00Z took the site down when the host machine failed, now fully resolved and with no bearing on the current recovery window.

## Contact

Queries about station 1442 are best raised in the network chat and we usually reply within a day.
