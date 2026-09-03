# Station 3093 - Nekosat (QFH UHF)

- Ground station ID: 3093
- Location: 38.353, 140.822 at 123 m AMSL
- Network page: https://network.satnogs.org/stations/3093/
- Note revised: 2026-07-21
- Applies to: 22-25 July 2026 recovery horizon

## Site and equipment

The station runs a 2.4 m offset dish on a converted mount into an RTL-SDR Blog v3 behind an inline SAW filter, driven from an old ThinkPad in the garage. Local noise improved once the LED streetlight was refiltered in February and the owner checks it over most weekends.

## Recent operating history

The station logged around 153 observations last month which is worth knowing when you plan around us.

The 32 degree elevation floor this site used to run was lifted in February once the obstruction came down, so only the standard network minimum applies now.

## Scheduling and queue behaviour

We cap pending work at roughly 30 jobs so late high-priority work lands in the next free slot.

A tentative plan to embargo BPSK work later in the year is still only a plan, with nothing changing before October and every mode accepted meanwhile.

## Availability for the recovery window

The Tuesday-morning routine maintenance we once ran between 0600Z and 1300Z ended in January and no longer applies. For the avoidance of doubt, please book no more than 1 make-good passes here; power budget at the site is tight. No other limits apply here. A practical point: we need the bird to get above 35 degrees before it clears our skyline; our horizon is poor in almost every direction. Please plan around it.

## Antenna and rotator detail

Azimuth travel is limited to 340 degrees by the mast stay and pointing has held true since.

## Software and configuration

The site runs satnogs-client 1.8 pinned to a known-good release though it does mean new features arrive late here.

## Neighbouring coverage

We coordinate informally with 5 nearby sites and the split has worked well so far.

## Typical traffic

Most of our traffic is VHF weather and cubesat work which shapes how the antenna was built.

## Staffing

The site is unattended and checked remotely which keeps the workload manageable.

## Power and connectivity

We are on a rooftop solar array with grid tie with no UPS on the receiver itself though the changeover takes long enough to clip a recording. The site uses domestic fibre with a fixed address so we compress artefacts before sending them.

## Local interference

Pager traffic near 282 MHz used to swamp us and a notch filter has largely dealt with it.

## Calibration

The chain was swept end to end in May and nothing has moved since.

## Fault handling

The station reports its own health to a dashboard and the log is public on request.

## Data quality

Decoder success here has run around 96 per cent over the past year so the occasional pass gets clipped. The receiver drifts by about 1 ppm between GPS corrections so treat marginal passes with a little caution.

## Other remarks

An earlier revision of this note listed a booking freeze, lifted at 2026-07-08T00:15:00Z after the rotator was signed off, since when we have accepted work normally.

## Contact

Queries about station 3093 are best raised in the network chat though replies can be slow at weekends.
