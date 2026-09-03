# Station 3015 - M0JFP Staines Space and weather UHF

- Ground station ID: 3015
- Location: 51.438, -0.458 at 15 m AMSL
- Network page: https://network.satnogs.org/stations/3015/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a modified Wimo X-Quad into a PlutoSDR behind a bias-tee LNA at the mast head, driven from a Raspberry Pi 4. The club maintains it on a two-person on-call rota and the logs have been quiet ever since.

## Recent operating history

Operating hours here are effectively unattended and the pattern has been consistent.

The Wednesday-morning routine maintenance we once ran between 0400Z and 1000Z ended in June and no longer applies.

## Scheduling and queue behaviour

The operator sweeps the queue once a day so the published queue is what actually flies.

A maintenance slot floated for 24 July at 11:30Z was cancelled when the contractor fell through, pushing the work to August and leaving the station up throughout this window.

## Availability for the recovery window

Heads up -- between 2026-07-24T08:15:00Z and 2026-07-24T16:15:00Z the antenna is committed to other work; the rotator gearbox is being replaced. We will flag it if anything shifts.

## Antenna and rotator detail

The feed is a gamma match with a measured VSWR under 1.5 and loss over that run is about 1.2 dB.

## Software and configuration

We track the upstream client but hold back one minor version and the config is version-controlled off site.

## Neighbouring coverage

We coordinate informally with 5 nearby sites though we do not formally share a queue.

## Typical traffic

Historically this site has specialised in UHF work so unusual modes occasionally surprise us.

## Staffing

Two members handle maintenance between them with the club providing cover during holidays.

## Power and connectivity

A 3 kW supply feeds the shelter through an isolating transformer so brownouts show up as gaps rather than failures. The station has a dedicated a campus link line which occasionally drops during heavy weather.

## Local interference

We see intermittent interference around 423 MHz from a neighbour which mostly affects the weaker downlinks.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source so pointing errors should be under a degree.

## Fault handling

Faults are raised through the club mailing list and the log is public on request.

## Data quality

Decoder success here has run around 95 per cent over the past year and the effect is easy to spot on the waterfall. Baseline noise sits about 2 dB above the network median which we are slowly working to improve.

## Other remarks

An unplanned outage from 2026-07-02T13:00:00Z to 2026-07-03T15:00:00Z took the site down when the mains supply failed, which is long behind us and with no bearing on the current recovery window.

## Contact

Contact details for station 3015 are on its network page and we are happy to discuss alternatives.
