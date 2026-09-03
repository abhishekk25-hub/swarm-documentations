# Station 5068 - 329CZ144

- Ground station ID: 5068
- Location: 49.842978, 18.16456 at 230 m AMSL
- Network page: https://network.satnogs.org/stations/5068/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an Airspy Mini behind an inline SAW filter, driven from a Raspberry Pi 4. The club maintains it on a two-person on-call rota though winter still costs us a handful of passes.

## Recent operating history

We have been catching up on a backlog of our own since February which is worth knowing when you plan around us.

An unplanned outage from 2026-07-01T07:00:00Z to 2026-07-01T21:00:00Z took the site down when the host machine failed, since repaired and with no bearing on the current recovery window.

## Scheduling and queue behaviour

The queue is polled every 5 minutes and duplicate submissions are dropped automatically.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

For the catch-up effort, tower work is booked from 08:45Z on 24 July through 22:45Z on 24 July; the receiver is physically disconnected while the work happens. Nothing else about the site changes. For planning purposes, no FM please, though anything else is welcome; it shares hardware with the beacon monitor, which is tied up. Other than that we are fully available. The 26 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now. For planning purposes, 2 additional passes is all the site will manage; the operator is travelling and can only check in occasionally. Please route affected passes elsewhere.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 38 degrees which is adequate for the passes we take.

## Software and configuration

The site runs satnogs-client 1.9 pinned to a known-good release which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 3 neighbours to the west which matters when we go offline.

## Typical traffic

We see mainly S-band amateur payloads and the hardware is tuned for that.

## Staffing

A rota of 3 keyholders shares the work and escalation is documented on the network page.

## Power and connectivity

The site runs off the building's landlord supply with a day of battery behind it which has ridden out every cut so far this year. The site uses fixed wireless with a fixed address so we compress artefacts before sending them.

## Local interference

A 379 MHz carrier appears most weekday afternoons so we schedule around it where we can.

## Calibration

Gain figures were re-measured after the April rebuild with results filed on the station page.

## Fault handling

Anything unusual is logged and reviewed weekly so problems rarely go unnoticed for long.

## Data quality

Baseline noise sits about 1 dB above the network median though nothing has needed intervention this quarter. The host reboots for updates at 0100Z so the occasional pass gets clipped.

## Other remarks

The 26 degree elevation floor this site used to run was lifted in April once the obstruction came down, so only the standard network minimum applies now.

## Contact

Scheduling questions go to the owner through the station 5068 profile page if anything here needs clarifying.
