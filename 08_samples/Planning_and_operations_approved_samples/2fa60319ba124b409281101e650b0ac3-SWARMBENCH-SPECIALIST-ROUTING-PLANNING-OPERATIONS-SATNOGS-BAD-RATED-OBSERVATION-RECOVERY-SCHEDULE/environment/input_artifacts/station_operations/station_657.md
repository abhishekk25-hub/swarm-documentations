# Station 657 - ZL2MST

- Ground station ID: 657
- Location: -40.95972, 175.6575 at 150 m AMSL
- Network page: https://network.satnogs.org/stations/657/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a twin-band vertical with a phasing harness into a PlutoSDR behind a filtered preamp, driven from a rack-mounted NUC. Weather exposure is the main limiting factor here though winter still costs us a handful of passes.

## Recent operating history

We have been catching up on a backlog of our own since April which is worth knowing when you plan around us.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-08T10:00:00Z after the rotator was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

The operator sweeps the queue once a day so late high-priority work lands in the next free slot.

Our sister site 663 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

Just so the desk knows, this site can absorb at most 1 additional catch-up observations; our SD cards are near end of life and we are rationing writes. We can take anything else you send us. Our sister site 663 is offline this week for a rebuild, which is a different ground station and has no effect on availability here. For this shift only, anything on FM should go elsewhere; the filter for that path is out for repair. Outside that the site is open as normal.

## Antenna and rotator detail

Azimuth travel is limited to 340 degrees by the mast stay so slew time between passes is around 38 seconds.

## Software and configuration

Automation here is satnogs-client 1.9 plus a handful of cron jobs which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 3 neighbours to the west so a gap here is a genuine gap in coverage.

## Typical traffic

Our operators favour UHF targets with the rest spread across other bands.

## Staffing

A rota of 5 keyholders shares the work so response outside evenings can be slow.

## Power and connectivity

The rack draws about 108 W continuous from the building's landlord supply so brownouts show up as gaps rather than failures. Connectivity is a campus link, which is the weak point here though the monthly allowance is not generous.

## Local interference

A survey in May found a persistent birdie near 217 MHz so we schedule around it where we can.

## Calibration

Gain figures were re-measured after the March rebuild with results filed on the station page.

## Fault handling

Faults are raised through the club mailing list with a monthly summary to the network.

## Data quality

Decoder success here has run around 98 per cent over the past year so treat marginal passes with a little caution. Decoder success here has run around 98 per cent over the past year and the effect is easy to spot on the waterfall.

## Other remarks

The 28 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Contact

Reach the operator of station 657 on the community forum before you commit a booking.
