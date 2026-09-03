# Station 1519 - Not Quite ESL

- Ground station ID: 1519
- Location: 38.58, -90 at 175 m AMSL
- Network page: https://network.satnogs.org/stations/1519/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an RTL-SDR v4 behind a cavity filter ahead of the receiver, driven from a rack-mounted NUC. Weather exposure is the main limiting factor here which suits the unattended operating we do here.

## Recent operating history

The station logged around 211 observations last month which is worth knowing when you plan around us.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

The queue is polled every 10 minutes so late high-priority work lands in the next free slot.

An unplanned outage from 2026-07-02T17:00:00Z to 2026-07-03T02:00:00Z took the site down when the network link failed, now fully resolved and with no bearing on the current recovery window.

## Availability for the recovery window

Station 1519 has nothing binding to declare for this window. Normal scheduling rules apply.

## Antenna and rotator detail

Elevation is fixed and the array is trimmed to 25 degrees which suits our mostly-overhead traffic.

## Software and configuration

Scheduling is driven by satnogs-client 1.8 with local patches and the config is version-controlled off site.

## Neighbouring coverage

This site sits inside a cluster of 3 stations so handing work over is usually straightforward.

## Typical traffic

Roughly 75 per cent of our passes are UHF and the hardware is tuned for that.

## Staffing

The site is unattended and checked remotely and escalation is documented on the network page.

## Power and connectivity

Everything here is fed from the club's metered feed via a residual-current breaker though the changeover takes long enough to clip a recording. We backhaul over a campus link from the mast to the house and latency has never affected scheduling.

## Local interference

Broadband hash from a nearby installation peaks around 199 MHz which the operator re-checks each quarter.

## Calibration

The chain was swept end to end in April and drift since has been within tolerance.

## Fault handling

The station reports its own health to a dashboard and response is usually the same evening.

## Data quality

Decoder success here has run around 88 per cent over the past year which we are slowly working to improve. Decoder success here has run around 88 per cent over the past year so treat marginal passes with a little caution.

## Other remarks

The 22 degree elevation floor this site used to run was lifted in May once the obstruction came down, so only the standard network minimum applies now.

## Contact

Contact details for station 1519 are on its network page and we usually reply within a day.
