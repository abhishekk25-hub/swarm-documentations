# Station 3590 - EuroSpaceHub-UCM

- Ground station ID: 3590
- Location: 39.569, -3.186 at 668 m AMSL
- Network page: https://network.satnogs.org/stations/3590/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a stacked dipole array into a HackRF One behind a switched attenuator for strong passes, driven from a Raspberry Pi 4. The mast was re-aligned in April after a storm though winter still costs us a handful of passes.

## Recent operating history

Volunteers rebuilt the feed arrangement in April though we do review anything anomalous.

An unplanned outage from 2026-06-07T19:00:00Z to 2026-06-08T15:00:00Z took the site down when the host machine failed, closed out at the time and with no bearing on the current recovery window.

## Scheduling and queue behaviour

We run a conservative queue depth of about 60 with rejections reported straight back to the network.

A tentative plan to embargo LRPT work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Availability for the recovery window

The main thing is that assume zero availability from us across the entire horizon; the mast is down for structural repair. Anything outside that scope is fine.

## Antenna and rotator detail

Azimuth travel is limited to 355 degrees by the mast stay and loss over that run is about 1.2 dB.

## Software and configuration

Automation here is the stock Raspbian image plus a handful of cron jobs though it does mean new features arrive late here.

## Neighbouring coverage

Our footprint overlaps 4 neighbours to the south which matters when we go offline.

## Typical traffic

We see mainly UHF amateur payloads which shapes how the antenna was built.

## Staffing

Day-to-day operation is fully automated though nobody is on site during the week.

## Power and connectivity

A 5 kW supply feeds the shelter through an isolating transformer and consumption has been stable since the rebuild. Connectivity is a 4G modem, which is the weak point here so large waterfall uploads queue up overnight.

## Local interference

A 248 MHz carrier appears most weekday afternoons so we schedule around it where we can.

## Calibration

Rotator alignment was re-surveyed in April and drift since has been within tolerance.

## Fault handling

Anything unusual is logged and reviewed weekly with a monthly summary to the network.

## Data quality

The host reboots for updates at 0300Z which we are slowly working to improve. Decoder success here has run around 93 per cent over the past year so treat marginal passes with a little caution.

## Other remarks

A maintenance slot floated for 24 July at 02:30Z was cancelled when the spare preamp fell through, pushing the work to August and leaving the station up throughout this window.

## Contact

Station 3590 is reachable through the usual operator channels and we usually reply within a day.
