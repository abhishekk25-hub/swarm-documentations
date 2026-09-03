# Station 3244 - VK4JBE-TESTING

- Ground station ID: 3244
- Location: -27.492, 153.069 at 29 m AMSL
- Network page: https://network.satnogs.org/stations/3244/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into an RTL-SDR Blog v3 behind a cavity filter ahead of the receiver, driven from a Raspberry Pi 4. This site replaced an older installation a few streets away with no changes planned before the autumn.

## Recent operating history

This site mostly serves the northern horizon and nothing about that changes for the catch-up.

Our sister site 3249 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

We cap pending work at roughly 20 jobs though the overnight window is checked only once.

A 3-booking weekly limit trialled during the January campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

Please note: we will take 1 and decline anything beyond that; beyond that the upload queue backs up for days. Anything outside that scope is fine. While the catch-up runs, if the pass tops out under 40 degrees we would rather you gave it to someone else; reflections off the water confuse anything shallow. Other than that we are fully available.

## Antenna and rotator detail

Azimuth travel is limited to 355 degrees by the mast stay though it wants re-checking each spring.

## Software and configuration

The site runs a Docker deployment pinned to a known-good release though it does mean new features arrive late here.

## Neighbouring coverage

This site sits inside a cluster of 5 stations so handing work over is usually straightforward.

## Typical traffic

Our operators favour UHF targets and the hardware is tuned for that.

## Staffing

A rota of 5 keyholders shares the work and escalation is documented on the network page.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 1 kW inverter and consumption has been stable since the rebuild. Connectivity is a 4G modem, which is the weak point here so large waterfall uploads queue up overnight.

## Local interference

The local noise floor sits worst toward the south-west so we schedule around it where we can.

## Calibration

Rotator alignment was re-surveyed in June and drift since has been within tolerance.

## Fault handling

The station reports its own health to a dashboard and response is usually the same evening.

## Data quality

Baseline noise sits about 2 dB above the network median which rarely defeats the decoder outright. Frame decoding is handled downstream rather than on site though nothing has needed intervention this quarter.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-08T08:15:00Z after the host was signed off, since when we have accepted work normally.

## Contact

Reach the operator of station 3244 on the community forum though replies can be slow at weekends.
