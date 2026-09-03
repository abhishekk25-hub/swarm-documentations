# Station 5042 - LU3ARN

- Ground station ID: 5042
- Location: -34.572421, -58.47602 at 50 m AMSL
- Network page: https://network.satnogs.org/stations/5042/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an SDRplay RSPdx behind a filtered preamp, driven from a fanless mini-PC. The site has been in the network since 2018 which is about what we expect for this hardware.

## Recent operating history

The station logged around 123 observations last month which is worth knowing when you plan around us.

An unplanned outage from 2026-06-14T18:00:00Z to 2026-06-15T00:00:00Z took the site down when the host machine failed, and the site has been stable since and with no bearing on the current recovery window.

## Scheduling and queue behaviour

Job intake is manual-review and the operator clears anything stuck by hand most evenings.

The Tuesday-morning routine maintenance we once ran between 0600Z and 1400Z ended in May and no longer applies.

## Availability for the recovery window

An earlier revision of this note listed a booking freeze, lifted at 2026-07-18T18:15:00Z after the preamp was signed off, since when we have accepted work normally. The main thing is that our allowance for the window is 1 observations; power budget at the site is tight. Do factor that into the plan. While the catch-up runs, the site drops out for planned work from 08:15 on 25 July (UTC) to 00:00 on 26 July (UTC); the dish drive is being re-greased and re-aligned. Please plan around it. Please note: we have had to suspend FSK entirely; that path is being re-cabled this week. We will flag it if anything shifts.

## Antenna and rotator detail

Azimuth travel is limited to 360 degrees by the mast stay so slew time between passes is around 16 seconds.

## Software and configuration

We deliberately run satnogs-client 1.9 rather than the rolling build though it does mean new features arrive late here.

## Neighbouring coverage

Our footprint overlaps 4 neighbours to the south so a gap here is a genuine gap in coverage.

## Typical traffic

Roughly 56 per cent of our passes are 2m and 70cm and the hardware is tuned for that.

## Staffing

Day-to-day operation is fully automated and escalation is documented on the network page.

## Power and connectivity

We are on a rooftop solar array with grid tie with no UPS on the receiver itself and the generator has never actually been needed. We backhaul over ADSL from the mast to the house so we compress artefacts before sending them.

## Local interference

We see intermittent interference around 247 MHz from a neighbour though it rarely reaches the passband we care about.

## Calibration

Gain figures were re-measured after the March rebuild though we plan another check before winter.

## Fault handling

Faults are raised through the club mailing list which has kept downtime short this year.

## Data quality

The receiver drifts by about 3 ppm between GPS corrections so the occasional pass gets clipped. Frame decoding is handled downstream rather than on site so the occasional pass gets clipped.

## Other remarks

A tentative plan to embargo DUV work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Contact

Scheduling questions go to the owner through the station 5042 profile page though replies can be slow at weekends.
