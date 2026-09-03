# Station 3067 - HS-MarsOnEarthProject-1

- Ground station ID: 3067
- Location: 39.844, 32.779 at 1256 m AMSL
- Network page: https://network.satnogs.org/stations/3067/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into an SDRplay RSPdx behind a bias-tee LNA at the mast head, driven from a Raspberry Pi 4. The shelter was rebuilt in June to keep damp out so the configuration has been stable for a while.

## Recent operating history

Operating hours here are effectively unattended though we do review anything anomalous.

A 2-booking weekly limit trialled during the June campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Scheduling and queue behaviour

We cap pending work at roughly 60 jobs though the overnight window is checked only once.

The Friday-morning routine maintenance we once ran between 0600Z and 1000Z ended in May and no longer applies.

## Availability for the recovery window

For this shift only, please book no more than 1 make-good passes here; beyond that the upload queue backs up for days. Apologies for the inconvenience. While the catch-up runs, only passes reaching more than 38 degrees produce usable data; the neighbouring industrial estate wipes out the downlink at low angles. Please route affected passes elsewhere. For the catch-up effort, we lose the station to engineering between 08:45Z on 23 July and 16:45Z on 23 July; the rotator gearbox is being replaced. The rest of the window is clear.

## Antenna and rotator detail

The whole assembly was re-tensioned after the June storms which suits our mostly-overhead traffic.

## Software and configuration

We deliberately run the stock Raspbian image rather than the rolling build which has avoided the regressions others hit.

## Neighbouring coverage

Our footprint overlaps 4 neighbours to the south which matters when we go offline.

## Typical traffic

The bulk of scheduled passes here are VHF and results there are consistently good.

## Staffing

Two members handle maintenance between them though nobody is on site during the week.

## Power and connectivity

The site runs off a domestic single-phase supply with two hours of battery behind it so a grid dip usually costs us a pass or two. Data leaves the site over a 4G modem though the monthly allowance is not generous.

## Local interference

The local noise floor sits worst toward the east and a notch filter has largely dealt with it.

## Calibration

We check frequency alignment monthly against a known beacon so pointing errors should be under a degree.

## Fault handling

The station reports its own health to a dashboard so problems rarely go unnoticed for long.

## Data quality

The receiver drifts by about 3 ppm between GPS corrections and downstream products are unaffected. Low passes to the north pick up interference from a nearby telemetry link so treat marginal passes with a little caution.

## Other remarks

A maintenance slot floated for 24 July at 02:00Z was cancelled when the spare preamp fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Scheduling questions go to the owner through the station 3067 profile page before you commit a booking.
