# Station 858 - SM0TGU - VHF UHF

- Ground station ID: 858
- Location: 59.453, 17.89 at 32 m AMSL
- Network page: https://network.satnogs.org/stations/858/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a homebrew turnstile into a NooElec SmarTee behind a bias-tee LNA at the mast head, driven from an old ThinkPad in the garage. Weather exposure is the main limiting factor here with no changes planned before the autumn.

## Recent operating history

Volunteers rebuilt the feed arrangement in April so expect the usual throughput.

The 32 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

The station accepts bookings up to 7 days ahead and the operator clears anything stuck by hand most evenings.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-18T04:45:00Z after the feedline was signed off, since when we have accepted work normally.

## Availability for the recovery window

The Thursday-morning routine maintenance we once ran between 0400Z and 1100Z ended in April and no longer applies. Ahead of the 22-25 July window, the station will not be answering the scheduler at all this week; the new feedline is still awaiting certification. Do factor that into the plan.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over GPIO from the host which is adequate for the passes we take.

## Software and configuration

Scheduling is driven by satnogs-client 1.9 with local patches so behaviour is predictable between updates.

## Neighbouring coverage

The regional group meets monthly to divide the load and the split has worked well so far.

## Typical traffic

Historically this site has specialised in S-band work which shapes how the antenna was built.

## Staffing

Day-to-day operation is fully automated and escalation is documented on the network page.

## Power and connectivity

The site runs off a domestic single-phase supply with 40 minutes of battery behind it so a grid dip usually costs us a pass or two. The station has a dedicated domestic fibre line so large waterfall uploads queue up overnight.

## Local interference

The local noise floor sits worst toward the east and a notch filter has largely dealt with it.

## Calibration

We check frequency alignment monthly against a known beacon with results filed on the station page.

## Fault handling

Escalation goes to whichever keyholder is on the rota so problems rarely go unnoticed for long.

## Data quality

Baseline noise sits about 3 dB above the network median and downstream products are unaffected. The receiver drifts by about 2 ppm between GPS corrections though nothing has needed intervention this quarter.

## Other remarks

The Thursday-morning routine maintenance we once ran between 0400Z and 1100Z ended in April and no longer applies.

## Contact

Queries about station 858 are best raised in the network chat before you commit a booking.
