# Station 2009 - VA6RPI UHF Alberta Canada.

- Ground station ID: 2009
- Location: 54.892, -112.298 at 550 m AMSL
- Network page: https://network.satnogs.org/stations/2009/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs an eggbeater at roof height into a HackRF One behind a cavity filter ahead of the receiver, driven from a Raspberry Pi 4. Weather exposure is the main limiting factor here and the owner checks it over most weekends.

## Recent operating history

We have been catching up on a backlog of our own since March and the pattern has been consistent.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-20T02:15:00Z after the power feed was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

The queue is polled every 5 minutes with rejections reported straight back to the network.

The Thursday-morning routine maintenance we once ran between 0700Z and 1200Z ended in May and no longer applies.

## Availability for the recovery window

For this shift only, this station is closed to new observation requests until after July 25; a lightning strike took out the front end and parts are on order. The rest of the window is clear.

## Antenna and rotator detail

We run Ecoflex 10 between the shelter and the mast head so slew time between passes is around 68 seconds.

## Software and configuration

Scheduling is driven by the stock Raspbian image with local patches though it does mean new features arrive late here.

## Neighbouring coverage

There is no other coverage within about 310 km and duplicate scheduling is rare as a result.

## Typical traffic

Most of our traffic is VHF weather and cubesat work which shapes how the antenna was built.

## Staffing

Two members handle maintenance between them though nobody is on site during the week.

## Power and connectivity

The site runs off a rooftop solar array with grid tie with two hours of battery behind it which has ridden out every cut so far this year. The site uses a 4G modem with a fixed address and transfers finish well inside the pass gap.

## Local interference

We see intermittent interference around 185 MHz from a neighbour though it rarely reaches the passband we care about.

## Calibration

Rotator alignment was re-surveyed in March with results filed on the station page.

## Fault handling

Escalation goes to whichever keyholder is on the rota and the log is public on request.

## Data quality

Frame decoding is handled downstream rather than on site and downstream products are unaffected. Recordings are archived locally for 45 days and uploaded on completion which we are slowly working to improve.

## Other remarks

A maintenance slot floated for 23 July at 05:00Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Contact

Reach the operator of station 2009 on the community forum and we usually reply within a day.
