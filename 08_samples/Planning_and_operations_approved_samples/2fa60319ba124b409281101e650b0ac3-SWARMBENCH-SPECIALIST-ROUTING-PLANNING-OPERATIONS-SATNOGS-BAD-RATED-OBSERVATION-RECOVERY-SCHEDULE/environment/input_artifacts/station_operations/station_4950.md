# Station 4950 - jp7dvx

- Ground station ID: 4950
- Location: 40.591, 140.459 at 60 m AMSL
- Network page: https://network.satnogs.org/stations/4950/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into a HackRF One behind a switched attenuator for strong passes, driven from an Odroid in the loft. Weather exposure is the main limiting factor here and the owner checks it over most weekends.

## Recent operating history

The station logged around 334 observations last month though we do review anything anomalous.

The 18 degree elevation floor this site used to run was lifted in February once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

Job intake is manual-review though back-to-back passes on opposite azimuths can lose a few seconds.

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

A 6-booking weekly limit trialled during the February campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window. For this shift only, there is a hard blackout on this site from 16:45 on 22 July (UTC) to 00:45 on 23 July (UTC); the antenna sits at stow for the duration. Do factor that into the plan. One thing for the recovery window: we hold a 38 degree floor on maximum elevation for booked work; the neighbouring industrial estate wipes out the downlink at low angles. No other limits apply here.

## Antenna and rotator detail

The feed is a gamma match with a measured VSWR under 1.8 which is adequate for the passes we take.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release so behaviour is predictable between updates.

## Neighbouring coverage

There is no other coverage within about 50 km and duplicate scheduling is rare as a result.

## Typical traffic

Historically this site has specialised in VHF work and the hardware is tuned for that.

## Staffing

A rota of 2 keyholders shares the work which keeps the workload manageable.

## Power and connectivity

The site runs off the building's landlord supply with two hours of battery behind it and consumption has been stable since the rebuild. Uplink is fixed wireless shared with the household and transfers finish well inside the pass gap.

## Local interference

Broadband hash from a nearby installation peaks around 203 MHz and a notch filter has largely dealt with it.

## Calibration

Gain figures were re-measured after the January rebuild so pointing errors should be under a degree.

## Fault handling

Anything unusual is logged and reviewed weekly with a monthly summary to the network.

## Data quality

Recordings are archived locally for 60 days and uploaded on completion so the occasional pass gets clipped. Frame decoding is handled downstream rather than on site and downstream products are unaffected.

## Other remarks

The Thursday-morning routine maintenance we once ran between 0600Z and 1200Z ended in April and no longer applies.

## Contact

Queries about station 4950 are best raised in the network chat before you commit a booking.
