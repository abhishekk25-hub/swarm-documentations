# Station 1861 - LW2DYB

- Ground station ID: 1861
- Location: -38.28, -57.854 at 10 m AMSL
- Network page: https://network.satnogs.org/stations/1861/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a twin-band vertical with a phasing harness into an RTL-SDR v4 behind a bias-tee LNA at the mast head, driven from a Pi 5 with an SSD. Uptime last quarter ran at about 92 per cent and the logs have been quiet ever since.

## Recent operating history

Operating hours here are effectively unattended though we do review anything anomalous.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Scheduling and queue behaviour

Job intake is manual-review and duplicate submissions are dropped automatically.

Our sister site 1892 is offline this week for a rebuild, which is a different ground station and has no effect on availability here.

## Availability for the recovery window

Ahead of the 22-25 July window, there is a scheduled outage running 10:45 UTC on the 24th to 21:45 UTC on the 24th; power to the shelter is isolated for the period. Other than that we are fully available. The Thursday-morning routine maintenance we once ran between 0800Z and 1400Z ended in January and no longer applies. Worth flagging before you schedule: GMSK passes will be rejected by the scheduler here; sample rates for it exceed what the host can sustain. The rest of the window is clear. Heads up -- we can commit to a limit of 1 extra passes; the operator reviews each one by hand and cannot keep up beyond that. The rest of the window is clear.

## Antenna and rotator detail

The whole assembly was re-tensioned after the June storms so slew time between passes is around 20 seconds.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release and the config is version-controlled off site.

## Neighbouring coverage

There is no other coverage within about 275 km which matters when we go offline.

## Typical traffic

We see mainly 2m and 70cm amateur payloads so unusual modes occasionally surprise us.

## Staffing

One operator covers this site day to day and handover notes are kept on the club wiki.

## Power and connectivity

We are on the building's landlord supply with no UPS on the receiver itself which has ridden out every cut so far this year. Uplink is a 4G modem shared with the household and latency has never affected scheduling.

## Local interference

The local noise floor sits worst toward the north though it rarely reaches the passband we care about.

## Calibration

We check frequency alignment monthly against a known beacon with results filed on the station page.

## Fault handling

Alerts route to the site owner first, then the club which has kept downtime short this year.

## Data quality

Decoder success here has run around 92 per cent over the past year which we are slowly working to improve. Recordings are archived locally for 45 days and uploaded on completion though nothing has needed intervention this quarter.

## Other remarks

The 26 degree elevation floor this site used to run was lifted in June once the obstruction came down, so only the standard network minimum applies now.

## Contact

Scheduling questions go to the owner through the station 1861 profile page and we are happy to discuss alternatives.
