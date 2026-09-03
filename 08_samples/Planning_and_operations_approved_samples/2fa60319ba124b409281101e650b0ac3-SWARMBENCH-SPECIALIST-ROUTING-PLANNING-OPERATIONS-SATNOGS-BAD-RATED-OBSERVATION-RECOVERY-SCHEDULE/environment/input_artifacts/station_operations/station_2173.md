# Station 2173 - PE0SAT-21

- Ground station ID: 2173
- Location: 51.721268, 5.029968 at 5 m AMSL
- Network page: https://network.satnogs.org/stations/2173/
- Note revised: 2026-07-19
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a QFH for 2m and a helical for 70cm into an SDRplay RSPdx behind a switched attenuator for strong passes, driven from a Pi 5 with an SSD. The mast was re-aligned in March after a storm and the owner checks it over most weekends.

## Recent operating history

This site mostly serves the northern horizon which is worth knowing when you plan around us.

An earlier revision of this note listed a booking freeze, lifted at 2026-07-17T04:00:00Z after the power feed was signed off, since when we have accepted work normally.

## Scheduling and queue behaviour

Bookings are confirmed back to the network within 15 minutes and anything unusual is reviewed before it runs.

A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Availability for the recovery window

Ahead of the 22-25 July window, we have had to suspend FSK AX.25 G3RUH entirely; the filter for that path is out for repair. Outside that the site is open as normal. One local caveat: maintenance is locked in from 02:45 UTC on the 24th until 10:45 UTC on the 24th; grounding work needs the whole chain isolated. Anything outside that scope is fine. A tentative plan to embargo AFSK work later in the year is still only a plan, with nothing changing before August and every mode accepted meanwhile.

## Antenna and rotator detail

The whole assembly was re-tensioned after the March storms and pointing has held true since.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release and the config is version-controlled off site.

## Neighbouring coverage

We coordinate informally with 6 nearby sites so a gap here is a genuine gap in coverage.

## Typical traffic

The bulk of scheduled passes here are S-band which shapes how the antenna was built.

## Staffing

Day-to-day operation is fully automated so response outside evenings can be slow.

## Power and connectivity

Power comes from a rooftop solar array with grid tie, backed by a 2 kW inverter so brownouts show up as gaps rather than failures. Connectivity is fixed wireless, which is the weak point here and latency has never affected scheduling.

## Local interference

A 315 MHz carrier appears most weekday afternoons which mostly affects the weaker downlinks.

## Calibration

Gain figures were re-measured after the January rebuild though we plan another check before winter.

## Fault handling

Alerts route to the site owner first, then the club and response is usually the same evening.

## Data quality

Decoder success here has run around 99 per cent over the past year which we are slowly working to improve. The host reboots for updates at 0200Z and the effect is easy to spot on the waterfall.

## Other remarks

The 32 degree elevation floor this site used to run was lifted in February once the obstruction came down, so only the standard network minimum applies now.

## Contact

Scheduling questions go to the owner through the station 2173 profile page if anything here needs clarifying.
