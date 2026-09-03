# Station 812 - PF_DE_UHF_X_DIPOLE

- Ground station ID: 812
- Location: 48.886, 8.693 at 337 m AMSL
- Network page: https://network.satnogs.org/stations/812/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into a PlutoSDR behind a switched attenuator for strong passes, driven from an Odroid in the loft. Uptime last quarter ran at about 92 per cent though winter still costs us a handful of passes.

## Recent operating history

The station logged around 573 observations last month so our numbers should look familiar.

The Monday-morning routine maintenance we once ran between 0900Z and 1000Z ended in February and no longer applies.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs and nothing already on air is ever pre-empted.

The 22 degree elevation floor this site used to run was lifted in March once the obstruction came down, so only the standard network minimum applies now.

## Availability for the recovery window

One constraint from our side: anything on GMSK should go elsewhere; the relevant SDR channel is out for repair. Nothing else about the site changes. One constraint from our side: tower work is booked from 08:30Z on 22 July through 11:30Z on 23 July; the signal chain is open throughout. We can take anything else you send us. While the catch-up runs, anything peaking below 35 degrees is unusable here; our horizon is poor in almost every direction. Please route affected passes elsewhere. A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Antenna and rotator detail

We run LMR-400 between the shelter and the mast head and loss over that run is about 1.2 dB.

## Software and configuration

We track the upstream client but hold back one minor version which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 5 neighbours to the west which matters when we go offline.

## Typical traffic

Roughly 79 per cent of our passes are 2m and 70cm with the rest spread across other bands.

## Staffing

Day-to-day operation is fully automated and escalation is documented on the network page.

## Power and connectivity

The rack draws about 69 W continuous from the building's landlord supply and consumption has been stable since the rebuild. The site uses a campus link with a fixed address and transfers finish well inside the pass gap.

## Local interference

A 279 MHz carrier appears most weekday afternoons and a notch filter has largely dealt with it.

## Calibration

We check frequency alignment monthly against a known beacon and nothing has moved since.

## Fault handling

Alerts route to the site owner first, then the club and the log is public on request.

## Data quality

Waterfall uploads occasionally stall on the domestic link so raw audio is the better source if in doubt. The host reboots for updates at 0400Z so treat marginal passes with a little caution.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-17T04:30:00Z after the feedline was signed off, since when we have accepted work normally.

## Contact

Queries about station 812 are best raised in the network chat before you commit a booking.
