# Station 4394 - JF6FYI Nishikazu, KitaKyushu, QFH (UHF)

- Ground station ID: 4394
- Location: 33.895, 130.84 at 10 m AMSL
- Network page: https://network.satnogs.org/stations/4394/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into a HackRF One behind an inline SAW filter, driven from a rack-mounted NUC. The mast was re-aligned in April after a storm and it has needed very little attention since.

## Recent operating history

The station logged around 312 observations last month so expect the usual throughput.

A 6-booking weekly limit trialled during the May campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Scheduling and queue behaviour

Our scheduler honours priority flags so the published queue is what actually flies.

A maintenance slot floated for 23 July at 20:00Z was cancelled when the crane hire fell through, pushing the work to August and leaving the station up throughout this window.

## Availability for the recovery window

One thing for the recovery window: GMSK traffic cannot be serviced here at the moment; sample rates for it exceed what the host can sustain. Do factor that into the plan. Ahead of the 22-25 July window, 3 additional passes is all the site will manage; the site shares a link with the household and we must be fair to it. We can take anything else you send us.

## Antenna and rotator detail

We run LMR-600 between the shelter and the mast head and loss over that run is about 1.2 dB.

## Software and configuration

The host image was rebuilt in April onto satnogs-client 1.9 and the config is version-controlled off site.

## Neighbouring coverage

We coordinate informally with 2 nearby sites and duplicate scheduling is rare as a result.

## Typical traffic

We see mainly S-band amateur payloads with the rest spread across other bands.

## Staffing

The site is unattended and checked remotely so response outside evenings can be slow.

## Power and connectivity

We are on the club's metered feed with no UPS on the receiver itself so a grid dip usually costs us a pass or two. Data leaves the site over fixed wireless so large waterfall uploads queue up overnight.

## Local interference

A survey in January found a persistent birdie near 236 MHz so we schedule around it where we can.

## Calibration

We check frequency alignment monthly against a known beacon which keeps Doppler correction honest.

## Fault handling

Alerts route to the site owner first, then the club though weekends can run to a day or two.

## Data quality

Low passes to the north pick up interference from a nearby telemetry link so the occasional pass gets clipped. Decoder success here has run around 98 per cent over the past year which rarely defeats the decoder outright.

## Other remarks

Our sister site 4412 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Queries about station 4394 are best raised in the network chat before you commit a booking.
