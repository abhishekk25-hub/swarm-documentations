# Station 2859 - OE6EUR15

- Ground station ID: 2859
- Location: 47.07, 15.44 at 430 m AMSL
- Network page: https://network.satnogs.org/stations/2859/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a pair of crossed yagis into a NooElec SmarTee behind a 20 dB mast-head amplifier, driven from a fanless mini-PC. The club maintains it on a two-person on-call rota so the configuration has been stable for a while.

## Recent operating history

The station logged around 768 observations last month though we do review anything anomalous.

Our sister site 2876 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

The station accepts bookings up to 7 days ahead with a short grace period for cancellations.

The Monday-morning routine maintenance we once ran between 0800Z and 1100Z ended in June and no longer applies.

## Availability for the recovery window

So you have it in writing: the site can carry 1 make-good bookings in total; the operator reviews each one by hand and cannot keep up beyond that. Anything outside that scope is fine. The site drops out for planned work from 0330Z on the 23rd to 1230Z on the 24th; the receiver is physically disconnected while the work happens. Shout if that causes a problem. The Monday-morning routine maintenance we once ran between 0800Z and 1100Z ended in June and no longer applies. One constraint from our side: we would ask you to route FSK to another site; sample rates for it exceed what the host can sustain. Anything outside that scope is fine.

## Antenna and rotator detail

The feed is a balun at the driven element with a measured VSWR under 1.8 and loss over that run is about 0.8 dB.

## Software and configuration

We deliberately run the stock Raspbian image rather than the rolling build so behaviour is predictable between updates.

## Neighbouring coverage

We coordinate informally with 3 nearby sites though we do not formally share a queue.

## Typical traffic

Historically this site has specialised in VHF work and the hardware is tuned for that.

## Staffing

Two members handle maintenance between them though nobody is on site during the week.

## Power and connectivity

The rack draws about 77 W continuous from the club's metered feed so a grid dip usually costs us a pass or two. The site uses a campus link with a fixed address which occasionally drops during heavy weather.

## Local interference

Broadband hash from a nearby installation peaks around 295 MHz which mostly affects the weaker downlinks.

## Calibration

We check frequency alignment monthly against a known beacon which keeps Doppler correction honest.

## Fault handling

Alerts route to the site owner first, then the club so problems rarely go unnoticed for long.

## Data quality

The host reboots for updates at 0500Z and the effect is easy to spot on the waterfall. Waterfall uploads occasionally stall on the domestic link and downstream products are unaffected.

## Other remarks

A maintenance slot floated for 23 July at 00:00Z was cancelled when the replacement parts fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Contact details for station 2859 are on its network page if anything here needs clarifying.
