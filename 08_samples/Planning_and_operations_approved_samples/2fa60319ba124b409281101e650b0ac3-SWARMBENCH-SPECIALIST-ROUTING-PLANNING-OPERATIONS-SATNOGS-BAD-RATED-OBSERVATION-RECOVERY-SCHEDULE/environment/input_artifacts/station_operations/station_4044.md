# Station 4044 - South Australia - UHF

- Ground station ID: 4044
- Location: -33.9499962, 138.6333308 at 390 m AMSL
- Network page: https://network.satnogs.org/stations/4044/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a fixed zenith turnstile into an RTL-SDR Blog v3 behind a helical bandpass filter, driven from a fanless mini-PC. This site replaced an older installation a few streets away which suits the unattended operating we do here.

## Recent operating history

Volunteers rebuilt the feed arrangement in March so our numbers should look familiar.

The Friday-morning routine maintenance we once ran between 0800Z and 1200Z ended in January and no longer applies.

## Scheduling and queue behaviour

Our scheduler honours priority flags with a short grace period for cancellations.

A 8-booking weekly limit trialled during the May campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

One thing for the recovery window: we decline passes that do not clear 33 degrees at their highest point; the ridge to our south swallows low passes. Apologies for the inconvenience. A 8-booking weekly limit trialled during the May campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window. Before anything is booked, our ceiling for this exercise is 1 bookings; storage fills faster than we can offload. We remain open either side of it.

## Antenna and rotator detail

Azimuth travel is limited to 360 degrees by the mast stay which is adequate for the passes we take.

## Software and configuration

We track the upstream client but hold back one minor version so behaviour is predictable between updates.

## Neighbouring coverage

Our footprint overlaps 2 neighbours to the east though we do not formally share a queue.

## Typical traffic

Most of our traffic is S-band weather and cubesat work and the hardware is tuned for that.

## Staffing

Two members handle maintenance between them and handover notes are kept on the club wiki.

## Power and connectivity

We are on the building's landlord supply with no UPS on the receiver itself so brownouts show up as gaps rather than failures. Uplink is a campus link shared with the household which occasionally drops during heavy weather.

## Local interference

Broadband hash from a nearby installation peaks around 179 MHz and it is documented in our station notes upstream.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source and nothing has moved since.

## Fault handling

The operator is paged automatically on three consecutive failures so problems rarely go unnoticed for long.

## Data quality

Baseline noise sits about 4 dB above the network median and the effect is easy to spot on the waterfall. Decoder success here has run around 97 per cent over the past year though nothing has needed intervention this quarter.

## Other remarks

A maintenance slot floated for 25 July at 09:00Z was cancelled when the replacement parts fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Queries about station 4044 are best raised in the network chat and we are happy to discuss alternatives.
