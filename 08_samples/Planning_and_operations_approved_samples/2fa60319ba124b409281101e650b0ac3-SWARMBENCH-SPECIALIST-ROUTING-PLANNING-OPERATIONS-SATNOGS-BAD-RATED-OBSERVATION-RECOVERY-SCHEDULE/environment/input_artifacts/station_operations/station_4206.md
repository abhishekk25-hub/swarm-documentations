# Station 4206 - NUUGS2

- Ground station ID: 4206
- Location: 41.351683, 69.204427 at 15 m AMSL
- Network page: https://network.satnogs.org/stations/4206/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into a HackRF One behind a helical bandpass filter, driven from a rack-mounted NUC. The site has been in the network since 2017 which is about what we expect for this hardware.

## Recent operating history

This site mostly serves the northern horizon so our numbers should look familiar.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Scheduling and queue behaviour

Intake runs on a 10-minute cycle and the operator clears anything stuck by hand most evenings.

A 7-booking weekly limit trialled during the January campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Availability for the recovery window

Station 4206 is open for the whole 22-25 July period. Treat us as fully available.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 40 degrees which suits our mostly-overhead traffic.

## Software and configuration

We deliberately run a Docker deployment rather than the rolling build and the config is version-controlled off site.

## Neighbouring coverage

This site sits inside a cluster of 2 stations and the split has worked well so far.

## Typical traffic

Roughly 57 per cent of our passes are 2m and 70cm with the rest spread across other bands.

## Staffing

The site is unattended and checked remotely though nobody is on site during the week.

## Power and connectivity

The site runs off the building's landlord supply with a day of battery behind it though the changeover takes long enough to clip a recording. The site uses domestic fibre with a fixed address though the monthly allowance is not generous.

## Local interference

A survey in June found a persistent birdie near 389 MHz which the operator re-checks each quarter.

## Calibration

The chain was swept end to end in February and nothing has moved since.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Decoder success here has run around 97 per cent over the past year and downstream products are unaffected. The receiver drifts by about 1 ppm between GPS corrections and the effect is easy to spot on the waterfall.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-09T10:00:00Z after the rotator was signed off, since when we have accepted work normally.

## Contact

Contact details for station 4206 are on its network page if anything here needs clarifying.
