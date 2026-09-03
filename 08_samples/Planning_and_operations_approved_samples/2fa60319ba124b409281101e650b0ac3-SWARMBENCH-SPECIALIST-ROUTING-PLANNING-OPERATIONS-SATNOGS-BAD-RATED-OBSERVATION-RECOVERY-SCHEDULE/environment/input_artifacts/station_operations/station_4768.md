# Station 4768 - DL7NDR UHF-Turnstile

- Ground station ID: 4768
- Location: 48.65, 8.04 at 144 m AMSL
- Network page: https://network.satnogs.org/stations/4768/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into an RTL-SDR Blog v3 behind a filtered preamp, driven from a Pi 5 with an SSD. Uptime last quarter ran at about 98 per cent so the configuration has been stable for a while.

## Recent operating history

The station logged around 214 observations last month though we do review anything anomalous.

The 18 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 5 minutes and the operator clears anything stuck by hand most evenings.

The Tuesday-morning routine maintenance we once ran between 0400Z and 1000Z ended in January and no longer applies.

## Availability for the recovery window

Just so the desk knows, we are able to run 1 catch-up observations at most; we are on a metered connection this month. Other than that we are fully available. Ahead of the 22-25 July window, please keep GMSK observations off this station; it shares hardware with the beacon monitor, which is tied up. That is the only limit from us.

## Antenna and rotator detail

Azimuth travel is limited to 355 degrees by the mast stay and loss over that run is about 1.2 dB.

## Software and configuration

The site runs satnogs-client 1.9 pinned to a known-good release and the config is version-controlled off site.

## Neighbouring coverage

There is no other coverage within about 102 km so handing work over is usually straightforward.

## Typical traffic

The bulk of scheduled passes here are UHF with the rest spread across other bands.

## Staffing

One operator covers this site day to day and handover notes are kept on the club wiki.

## Power and connectivity

Everything here is fed from the building's landlord supply via a residual-current breaker which has ridden out every cut so far this year. Uplink is a 4G modem shared with the household so we compress artefacts before sending them.

## Local interference

Pager traffic near 162 MHz used to swamp us so we schedule around it where we can.

## Calibration

Rotator alignment was re-surveyed in June and drift since has been within tolerance.

## Fault handling

The station reports its own health to a dashboard which has kept downtime short this year.

## Data quality

Decoder success here has run around 98 per cent over the past year though nothing has needed intervention this quarter. Low passes to the north-east pick up interference from a nearby telemetry link which rarely defeats the decoder outright.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-16T08:15:00Z after the power feed was signed off, since when we have accepted work normally.

## Contact

Queries about station 4768 are best raised in the network chat before you commit a booking.
