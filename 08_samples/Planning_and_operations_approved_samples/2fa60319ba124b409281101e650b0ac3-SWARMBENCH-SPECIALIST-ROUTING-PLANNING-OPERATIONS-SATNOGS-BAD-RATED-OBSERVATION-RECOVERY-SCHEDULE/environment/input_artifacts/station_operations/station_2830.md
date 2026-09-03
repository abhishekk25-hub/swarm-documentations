# Station 2830 - SM0TGU - L and S-Band

- Ground station ID: 2830
- Location: 59.453, 17.89 at 32 m AMSL
- Network page: https://network.satnogs.org/stations/2830/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into an RTL-SDR v4 behind a 20 dB mast-head amplifier, driven from an old ThinkPad in the garage. Local noise improved once the solar inverter was refiltered in April which is about what we expect for this hardware.

## Recent operating history

We have been catching up on a backlog of our own since April though we do review anything anomalous.

Our sister site 2838 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Job intake is manual-review and nothing already on air is ever pre-empted.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

To save you a wasted slot, no FM please, though anything else is welcome; the filter for that path is out for repair. Do factor that into the plan. Just so the desk knows, 1 additional passes is all the site will manage; power budget at the site is tight. We can take anything else you send us.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 41 degrees so slew time between passes is around 34 seconds.

## Software and configuration

Scheduling is driven by a Docker deployment with local patches so behaviour is predictable between updates.

## Neighbouring coverage

The nearest other station is roughly 22 km away so handing work over is usually straightforward.

## Typical traffic

Roughly 50 per cent of our passes are UHF and results there are consistently good.

## Staffing

The site is unattended and checked remotely and escalation is documented on the network page.

## Power and connectivity

We are on a rooftop solar array with grid tie with no UPS on the receiver itself and consumption has been stable since the rebuild. We backhaul over domestic fibre from the mast to the house so we compress artefacts before sending them.

## Local interference

The local noise floor sits worst toward the south-west and a notch filter has largely dealt with it.

## Calibration

Gain figures were re-measured after the March rebuild and nothing has moved since.

## Fault handling

The station reports its own health to a dashboard so problems rarely go unnoticed for long.

## Data quality

Baseline noise sits about 4 dB above the network median and the effect is easy to spot on the waterfall. Decoder success here has run around 99 per cent over the past year and downstream products are unaffected.

## Other remarks

The Wednesday-morning routine maintenance we once ran between 0600Z and 1300Z ended in April and no longer applies.

## Contact

Reach the operator of station 2830 on the community forum before you commit a booking.
