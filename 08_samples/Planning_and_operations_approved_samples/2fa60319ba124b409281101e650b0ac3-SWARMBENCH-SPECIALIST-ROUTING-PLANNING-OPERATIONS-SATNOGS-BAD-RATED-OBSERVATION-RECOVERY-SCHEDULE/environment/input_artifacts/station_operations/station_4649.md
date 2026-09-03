# Station 4649 - BG7XTQ

- Ground station ID: 4649
- Location: 22.81024, 108.32949 at 76 m AMSL
- Network page: https://network.satnogs.org/stations/4649/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into a NooElec SmarTee behind a helical bandpass filter, driven from a Raspberry Pi 4. Local noise improved once the solar inverter was refiltered in March and it has needed very little attention since.

## Recent operating history

We have been catching up on a backlog of our own since March though we do review anything anomalous.

The 32 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

We run a conservative queue depth of about 60 and the rotator pre-positions a little ahead of AOS.

A maintenance slot floated for 25 July at 15:00Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Availability for the recovery window

So you have it in writing: we would ask you to route FSK to another site; that demodulator chain is mid-rebuild. Shout if that causes a problem. To save you a wasted slot, treat 30 degrees as the lowest culmination we can work with; the ridge to our south swallows low passes. We will flag it if anything shifts. Ahead of the 22-25 July window, between 13:45 UTC on the 22nd and 22:45 UTC on the 23rd the antenna is committed to other work; the antenna sits at stow for the duration. Nothing else about the site changes.

## Antenna and rotator detail

The feed is a balun at the driven element with a measured VSWR under 1.8 and loss over that run is about 2.1 dB.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release so behaviour is predictable between updates.

## Neighbouring coverage

Our footprint overlaps 6 neighbours to the north though we do not formally share a queue.

## Typical traffic

Our operators favour VHF targets with the rest spread across other bands.

## Staffing

A rota of 3 keyholders shares the work which keeps the workload manageable.

## Power and connectivity

We are on a rooftop solar array with grid tie with no UPS on the receiver itself which has ridden out every cut so far this year. Uplink is fixed wireless shared with the household and transfers finish well inside the pass gap.

## Local interference

We see intermittent interference around 209 MHz from a neighbour which mostly affects the weaker downlinks.

## Calibration

Gain figures were re-measured after the May rebuild and drift since has been within tolerance.

## Fault handling

Faults are raised through the club mailing list which has kept downtime short this year.

## Data quality

Decoder success here has run around 91 per cent over the past year and the effect is easy to spot on the waterfall. Frame decoding is handled downstream rather than on site so the occasional pass gets clipped.

## Other remarks

The Tuesday-morning routine maintenance we once ran between 0700Z and 1300Z ended in January and no longer applies.

## Contact

Queries about station 4649 are best raised in the network chat and we are happy to discuss alternatives.
