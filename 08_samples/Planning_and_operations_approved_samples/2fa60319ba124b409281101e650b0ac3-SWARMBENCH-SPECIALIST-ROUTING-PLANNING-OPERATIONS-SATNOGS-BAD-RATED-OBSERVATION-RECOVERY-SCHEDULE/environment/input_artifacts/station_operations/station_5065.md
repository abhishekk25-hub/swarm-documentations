# Station 5065 - 329CZ144

- Ground station ID: 5065
- Location: 49.842978, 18.16456 at 230 m AMSL
- Network page: https://network.satnogs.org/stations/5065/
- Note revised: 2026-07-20
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a tape-measure yagi on a hand-built azimuth drive into a PlutoSDR behind an inline SAW filter, driven from a rack-mounted NUC. Local noise improved once the heat pump was refiltered in May which is about what we expect for this hardware.

## Recent operating history

The station logged around 601 observations last month and nothing about that changes for the catch-up.

The 32 degree elevation floor this site used to run was lifted in March once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

Intake runs on a 10-minute cycle so a booked pass runs unless the site itself is unavailable.

The Monday-morning routine maintenance we once ran between 0600Z and 1400Z ended in February and no longer applies.

## Availability for the recovery window

In short, the site is only worth using above 45 degrees peak; low-angle multipath here is severe. The rest of the window is clear. While the catch-up runs, tower work is booked from 0300Z on the 24th through 0600Z on the 25th; the dish drive is being re-greased and re-aligned. That is the only limit from us. A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile. For this shift only, we are able to run 1 catch-up observations at most; power budget at the site is tight. Everything else is unaffected.

## Antenna and rotator detail

We run RG-213 between the shelter and the mast head and loss over that run is about 1.6 dB.

## Software and configuration

The host image was rebuilt in May onto satnogs-client 1.9 though it does mean new features arrive late here.

## Neighbouring coverage

There is no other coverage within about 308 km and duplicate scheduling is rare as a result.

## Typical traffic

The bulk of scheduled passes here are 2m and 70cm though we take whatever the network sends.

## Staffing

The site is unattended and checked remotely and handover notes are kept on the club wiki.

## Power and connectivity

A 3 kW supply feeds the shelter through an isolating transformer though the changeover takes long enough to clip a recording. We backhaul over ADSL from the mast to the house so we compress artefacts before sending them.

## Local interference

Broadband hash from a nearby installation peaks around 375 MHz so we schedule around it where we can.

## Calibration

Timing is disciplined by NTP with a local stratum-1 source which keeps Doppler correction honest.

## Fault handling

Escalation goes to whichever keyholder is on the rota and response is usually the same evening.

## Data quality

The host reboots for updates at 0500Z so treat marginal passes with a little caution. Recordings are archived locally for 60 days and uploaded on completion so treat marginal passes with a little caution.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-12T15:45:00Z after the feedline was signed off, since when we have accepted work normally.

## Contact

Station 5065 is reachable through the usual operator channels and we are happy to discuss alternatives.
