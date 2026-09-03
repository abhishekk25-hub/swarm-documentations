# Station 5049 - JF6FYI Nishikazu, KitaKyushu, 3-ele Yagi(UHF)

- Ground station ID: 5049
- Location: 33.895, 130.84 at 10 m AMSL
- Network page: https://network.satnogs.org/stations/5049/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into an RTL-SDR v4 behind an inline SAW filter, driven from a fanless mini-PC. The site has been in the network since 2021 which is about what we expect for this hardware.

## Recent operating history

The station logged around 620 observations last month which is worth knowing when you plan around us.

A 4-booking weekly limit trialled during the March campaign to manage upload costs finished with it, and no booking limit is in force for this recovery window.

## Scheduling and queue behaviour

The operator sweeps the queue once a day and duplicate submissions are dropped automatically.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-17T00:45:00Z after the host was signed off, since when we have accepted work normally.

## Availability for the recovery window

So you have it in writing: FSK passes will be rejected by the scheduler here; it shares hardware with the beacon monitor, which is tied up. Nothing else about the site changes.

## Antenna and rotator detail

The rotator is a home-built stepper drive driven over USB serial which is adequate for the passes we take.

## Software and configuration

Automation here is the stock Raspbian image plus a handful of cron jobs so a rebuild takes under an hour.

## Neighbouring coverage

There is no other coverage within about 20 km so handing work over is usually straightforward.

## Typical traffic

We see mainly UHF amateur payloads with the rest spread across other bands.

## Staffing

The station is run by 2 volunteers and handover notes are kept on the club wiki.

## Power and connectivity

Everything here is fed from a domestic single-phase supply via a residual-current breaker and consumption has been stable since the rebuild. We backhaul over domestic fibre from the mast to the house and latency has never affected scheduling.

## Local interference

We see intermittent interference around 189 MHz from a neighbour so we schedule around it where we can.

## Calibration

The chain was swept end to end in April and drift since has been within tolerance.

## Fault handling

Escalation goes to whichever keyholder is on the rota which has kept downtime short this year.

## Data quality

Low passes to the north pick up interference from a nearby telemetry link so the occasional pass gets clipped. Waterfall uploads occasionally stall on the domestic link and downstream products are unaffected.

## Other remarks

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Contact

Scheduling questions go to the owner through the station 5049 profile page though replies can be slow at weekends.
