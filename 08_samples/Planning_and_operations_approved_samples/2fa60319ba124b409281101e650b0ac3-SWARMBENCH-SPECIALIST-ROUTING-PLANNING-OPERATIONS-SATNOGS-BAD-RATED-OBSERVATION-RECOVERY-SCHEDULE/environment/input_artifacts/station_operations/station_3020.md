# Station 3020 - Jim UHF

- Ground station ID: 3020
- Location: 33.797628, -79.159123 at 12 m AMSL
- Network page: https://network.satnogs.org/stations/3020/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into a HackRF One behind a helical bandpass filter, driven from a Pi 5 with an SSD. Weather exposure is the main limiting factor here and the owner checks it over most weekends.

## Recent operating history

Operating hours here are effectively unattended and nothing about that changes for the catch-up.

Our sister site 3027 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Scheduling and queue behaviour

Scheduling here is fully automated with a short grace period for cancellations.

A maintenance slot floated for 23 July at 10:00Z was cancelled when the spare preamp fell through, pushing the work to September and leaving the station up throughout this window.

## Availability for the recovery window

For this shift only, every slot in the recovery period is unavailable to you; roof access is blocked by unrelated building work. We can take anything else you send us.

## Antenna and rotator detail

The rotator is a Yaesu G-5500 driven over GPIO from the host though it wants re-checking each spring.

## Software and configuration

We deliberately run satnogs-client 1.8 rather than the rolling build though it does mean new features arrive late here.

## Neighbouring coverage

The regional group meets monthly to divide the load so handing work over is usually straightforward.

## Typical traffic

We see mainly 2m and 70cm amateur payloads with the rest spread across other bands.

## Staffing

Day-to-day operation is fully automated and escalation is documented on the network page.

## Power and connectivity

The rack draws about 55 W continuous from the building's landlord supply and the generator has never actually been needed. Uplink is domestic fibre shared with the household so we compress artefacts before sending them.

## Local interference

A 190 MHz carrier appears most weekday afternoons though it rarely reaches the passband we care about.

## Calibration

The receiver was last calibrated against a GPSDO in June so pointing errors should be under a degree.

## Fault handling

The station reports its own health to a dashboard with a monthly summary to the network.

## Data quality

Low passes to the east pick up interference from a nearby telemetry link so the occasional pass gets clipped. Low passes to the north-east pick up interference from a nearby telemetry link so the occasional pass gets clipped.

## Other remarks

An unplanned outage from 2026-07-04T01:00:00Z to 2026-07-05T03:00:00Z took the site down when the network link failed, and the site has been stable since and with no bearing on the current recovery window.

## Contact

Contact details for station 3020 are on its network page and we are happy to discuss alternatives.
