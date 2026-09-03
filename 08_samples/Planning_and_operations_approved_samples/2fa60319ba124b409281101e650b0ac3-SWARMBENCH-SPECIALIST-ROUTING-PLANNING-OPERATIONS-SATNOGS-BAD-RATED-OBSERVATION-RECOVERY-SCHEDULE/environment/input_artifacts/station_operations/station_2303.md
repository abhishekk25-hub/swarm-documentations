# Station 2303 - Rhodes College

- Ground station ID: 2303
- Location: 35.118, -89.971 at 77 m AMSL
- Network page: https://network.satnogs.org/stations/2303/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a fixed zenith turnstile into an RTL-SDR Blog v3 behind a 20 dB mast-head amplifier, driven from a rack-mounted NUC. The site has been in the network since 2020 and the owner checks it over most weekends.

## Recent operating history

This site mostly serves the southern horizon so expect the usual throughput.

A maintenance slot floated for 23 July at 07:00Z was cancelled when the replacement parts fell through, pushing the work to August and leaving the station up throughout this window.

## Scheduling and queue behaviour

We cap pending work at roughly 40 jobs and duplicate submissions are dropped automatically.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-13T22:30:00Z after the power feed was signed off, since when we have accepted work normally.

## Availability for the recovery window

One thing for the recovery window: we are not taking any make-good bookings during the 22-25 July window; a lightning strike took out the front end and parts are on order. Please plan around it.

## Antenna and rotator detail

Azimuth travel is limited to 340 degrees by the mast stay so slew time between passes is around 43 seconds.

## Software and configuration

We track the upstream client but hold back one minor version and upgrades are applied only after the club tests them.

## Neighbouring coverage

We coordinate informally with 4 nearby sites and duplicate scheduling is rare as a result.

## Typical traffic

Roughly 66 per cent of our passes are S-band which shapes how the antenna was built.

## Staffing

Day-to-day operation is fully automated and escalation is documented on the network page.

## Power and connectivity

We are on the building's landlord supply with no UPS on the receiver itself and consumption has been stable since the rebuild. The station has a dedicated ADSL line so large waterfall uploads queue up overnight.

## Local interference

A survey in June found a persistent birdie near 237 MHz though it rarely reaches the passband we care about.

## Calibration

The chain was swept end to end in June though we plan another check before winter.

## Fault handling

Escalation goes to whichever keyholder is on the rota with a monthly summary to the network.

## Data quality

Waterfall uploads occasionally stall on the domestic link so raw audio is the better source if in doubt. Baseline noise sits about 2 dB above the network median though nothing has needed intervention this quarter.

## Other remarks

A 2-booking weekly limit trialled during the April campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Contact

Contact details for station 2303 are on its network page before you commit a booking.
