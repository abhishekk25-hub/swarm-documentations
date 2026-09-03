# Station 3433 - HA5MI

- Ground station ID: 3433
- Location: 47.508395, 18.989147 at 280 m AMSL
- Network page: https://network.satnogs.org/stations/3433/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into an RTL-SDR Blog v3 behind a helical bandpass filter, driven from a Raspberry Pi 4. The shelter was rebuilt in March to keep damp out with no changes planned before the autumn.

## Recent operating history

We have been catching up on a backlog of our own since March and the pattern has been consistent.

The 26 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

The queue is polled every 10 minutes and anything unusual is reviewed before it runs.

A maintenance slot floated for 25 July at 16:30Z was cancelled when the replacement parts fell through, pushing the work to September and leaving the station up throughout this window.

## Availability for the recovery window

One constraint from our side: no FSK AX.100 Mode 5 please, though anything else is welcome; the relevant SDR channel is out for repair. Nothing else about the site changes. Our sister site 3437 is offline this week for a rebuild, which is a different ground station and has no effect on availability here. Between 24 July at 08:00 UTC and 25 July at 06:00 UTC the antenna is committed to other work; the controller firmware is being reflashed. Other than that we are fully available. For the catch-up effort, anything peaking below 35 degrees is unusable here; the ridge to our south swallows low passes. Other than that we are fully available.

## Antenna and rotator detail

Azimuth travel is limited to 355 degrees by the mast stay which suits our mostly-overhead traffic.

## Software and configuration

Scheduling is driven by satnogs-client 1.8 with local patches so a rebuild takes under an hour.

## Neighbouring coverage

We coordinate informally with 5 nearby sites and the split has worked well so far.

## Typical traffic

Our operators favour VHF targets and the hardware is tuned for that.

## Staffing

One operator covers this site day to day and handover notes are kept on the club wiki.

## Power and connectivity

We are on a domestic single-phase supply with no UPS on the receiver itself though the changeover takes long enough to clip a recording. Connectivity is domestic fibre, which is the weak point here and transfers finish well inside the pass gap.

## Local interference

A survey in March found a persistent birdie near 431 MHz though it rarely reaches the passband we care about.

## Calibration

Rotator alignment was re-surveyed in January though we plan another check before winter.

## Fault handling

Alerts route to the site owner first, then the club with a monthly summary to the network.

## Data quality

Decoder success here has run around 91 per cent over the past year though nothing has needed intervention this quarter. Frame decoding is handled downstream rather than on site though nothing has needed intervention this quarter.

## Other remarks

A tentative plan to embargo DUV work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Contact

Scheduling questions go to the owner through the station 3433 profile page and we are happy to discuss alternatives.
