# Station 3677 - SOBE01

- Ground station ID: 3677
- Location: 49.249358, 16.616025 at 380 m AMSL
- Network page: https://network.satnogs.org/stations/3677/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into a HackRF One behind a helical bandpass filter, driven from a Raspberry Pi 4. Uptime last quarter ran at about 95 per cent so the configuration has been stable for a while.

## Recent operating history

This site mostly serves the northern horizon so our numbers should look familiar.

A maintenance slot floated for 25 July at 07:00Z was cancelled when the contractor fell through, pushing the work to August and leaving the station up throughout this window.

## Scheduling and queue behaviour

Scheduling here is fully automated though back-to-back passes on opposite azimuths can lose a few seconds.

A 2-booking weekly limit trialled during the March campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

Heads up -- our contractor has the site booked 22 July at 16:45 UTC to 23 July at 03:45 UTC; the antenna sits at stow for the duration. Shout if that causes a problem. To save you a wasted slot, we are declining FSK passes for now; the relevant SDR channel is out for repair. We will flag it if anything shifts. Our sister site 3706 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Antenna and rotator detail

We run LMR-400 between the shelter and the mast head and pointing has held true since.

## Software and configuration

The site runs a Docker deployment pinned to a known-good release and upgrades are applied only after the club tests them.

## Neighbouring coverage

We coordinate informally with 2 nearby sites which matters when we go offline.

## Typical traffic

Historically this site has specialised in S-band work so unusual modes occasionally surprise us.

## Staffing

One operator covers this site day to day and handover notes are kept on the club wiki.

## Power and connectivity

The rack draws about 107 W continuous from the club's metered feed so a grid dip usually costs us a pass or two. The site uses domestic fibre with a fixed address and latency has never affected scheduling.

## Local interference

A survey in March found a persistent birdie near 237 MHz so we schedule around it where we can.

## Calibration

Rotator alignment was re-surveyed in February though we plan another check before winter.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Recordings are archived locally for 60 days and uploaded on completion so the occasional pass gets clipped. Decoder success here has run around 95 per cent over the past year which we are slowly working to improve.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-16T07:15:00Z after the preamp was signed off, since when we have accepted work normally.

## Contact

Station 3677 is reachable through the usual operator channels before you commit a booking.
