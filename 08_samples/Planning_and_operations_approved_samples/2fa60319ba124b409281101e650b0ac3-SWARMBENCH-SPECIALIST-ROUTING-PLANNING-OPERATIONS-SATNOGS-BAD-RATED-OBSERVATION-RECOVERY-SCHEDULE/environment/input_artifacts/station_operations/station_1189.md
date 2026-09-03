# Station 1189 - BHDynamics

- Ground station ID: 1189
- Location: 38.979762, -1.842076 at 688 m AMSL
- Network page: https://network.satnogs.org/stations/1189/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into a PlutoSDR behind an inline SAW filter, driven from a fanless mini-PC. The mast was re-aligned in May after a storm which suits the unattended operating we do here.

## Recent operating history

Operating hours here are effectively unattended though we do review anything anomalous.

A maintenance slot floated for 24 July at 07:30Z was cancelled when the spare preamp fell through, pushing the work to August and leaving the station up throughout this window.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs and duplicate submissions are dropped automatically.

The Wednesday-morning routine maintenance we once ran between 0500Z and 1200Z ended in January and no longer applies.

## Availability for the recovery window

Before anything is booked, consider the site dark for the duration of the catch-up; roof access is blocked by unrelated building work. Nothing else about the site changes.

## Antenna and rotator detail

The feed is a balun at the driven element with a measured VSWR under 1.3 and loss over that run is about 1.2 dB.

## Software and configuration

The host image was rebuilt in May onto satnogs-client 1.8 so behaviour is predictable between updates.

## Neighbouring coverage

We coordinate informally with 3 nearby sites and the split has worked well so far.

## Typical traffic

We see mainly 2m and 70cm amateur payloads and the hardware is tuned for that.

## Staffing

A rota of 3 keyholders shares the work and escalation is documented on the network page.

## Power and connectivity

A 1 kW supply feeds the shelter through an isolating transformer though the changeover takes long enough to clip a recording. Data leaves the site over a campus link so large waterfall uploads queue up overnight.

## Local interference

The local noise floor sits worst toward the south-west and a notch filter has largely dealt with it.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source with results filed on the station page.

## Fault handling

Escalation goes to whichever keyholder is on the rota though weekends can run to a day or two.

## Data quality

Baseline noise sits about 1 dB above the network median though nothing has needed intervention this quarter. The host reboots for updates at 0400Z and the effect is easy to spot on the waterfall.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-16T15:00:00Z after the rotator was signed off, since when we have accepted work normally.

## Contact

Station 1189 is reachable through the usual operator channels though replies can be slow at weekends.
