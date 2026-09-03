# Station 3715 - Gooseberry_Hill

- Ground station ID: 3715
- Location: -31.951, 116.04 at 135 m AMSL
- Network page: https://network.satnogs.org/stations/3715/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an RTL-SDR v4 behind a helical bandpass filter, driven from a fanless mini-PC. This site replaced an older installation a few streets away which suits the unattended operating we do here.

## Recent operating history

The station logged around 663 observations last month and nothing about that changes for the catch-up.

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Scheduling and queue behaviour

Job intake is manual-review and nothing already on air is ever pre-empted.

A maintenance slot floated for 23 July at 17:30Z was cancelled when the contractor fell through, pushing the work to September and leaving the station up throughout this window.

## Availability for the recovery window

Ahead of the 22-25 July window, FSK traffic cannot be serviced here at the moment; that path is being re-cabled this week. The rest of the window is clear. Treat 40 degrees as the lowest culmination we can work with; our horizon is poor in almost every direction. Do factor that into the plan. A 8-booking weekly limit trialled during the February campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window. Just so the desk knows, we lose the station to engineering between 2026-07-22T07:45:00Z and 2026-07-22T18:45:00Z; the rotator gearbox is being replaced. Please plan around it.

## Antenna and rotator detail

Azimuth travel is limited to 350 degrees by the mast stay and pointing has held true since.

## Software and configuration

Automation here is satnogs-client 1.9 plus a handful of cron jobs though it does mean new features arrive late here.

## Neighbouring coverage

The nearest other station is roughly 47 km away and duplicate scheduling is rare as a result.

## Typical traffic

Roughly 87 per cent of our passes are S-band which shapes how the antenna was built.

## Staffing

One operator covers this site day to day with the club providing cover during holidays.

## Power and connectivity

The rack draws about 127 W continuous from a rooftop solar array with grid tie so a grid dip usually costs us a pass or two. Connectivity is a campus link, which is the weak point here so large waterfall uploads queue up overnight.

## Local interference

The local noise floor sits worst toward the west which mostly affects the weaker downlinks.

## Calibration

The receiver was last calibrated against a GPSDO in April which keeps Doppler correction honest.

## Fault handling

Faults are raised through the club mailing list so problems rarely go unnoticed for long.

## Data quality

Frame decoding is handled downstream rather than on site so the occasional pass gets clipped. The host reboots for updates at 0300Z though nothing has needed intervention this quarter.

## Other remarks

Our sister site 3731 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Contact

Reach the operator of station 3715 on the community forum if anything here needs clarifying.
