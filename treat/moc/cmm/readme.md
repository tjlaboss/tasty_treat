# cmm

This is a sub-module of treat.moc providing classes and pre-calculated data
for the correction of multigroup cross sections via the
Cumulative Migration Method (CMM).

## Theory

For an explanation of the method, see:
[Cumulative migration method for computing rigorous diffusion coefficients and
transport cross sections from Monte Carlo](https://scholar.google.com/scholar?hl=en&as_sdt=0%2C22&q=Cumulative+migration+method+for+computing+rigorous+diffusion+coefficients+and+transport+cross+sections+from+Monte+Carlo&btnG)
(Liu et. al.).

The CMM method provides us groupwise diffusion coefficients in the transverse
(xy) direction and the axial (z) direction. We then take the ratio of the
transverse diffusion coefficient to the standard flux-limited definition.
The reciprocal of this is the ratio of transport cross sections, because

    $ \D_g = \frac{ 1 }{ 3 \Sigma_{tr, g} } $

That ratio is then used to correct the transport cross sections and the
in-group scatter cross sections appropriately.

## Data

### Elements

Data is provided for 3 types of elements:
  - fuel
  - fueled control rod element w/ graphite follower inserted
  - fueled control rod element w/ B4C poison inserted

Most of the core elements, including all of those used in TREAT'S
Minimum Critical Mass (MCM) core, can be described by the "fuel" profile with
reasonble accuracy.

Any unusual types, such as the access hole assemblies used in the M8Cal
configuration, will need to be tallied in their own models.

### Energy Groups

Correction factors are provided for the **11**-group 'TREAT' and
**25**-group 'CASMO' structures provided in moc.energy_groups.

Any additional energy group strucutes will need to be tallied in their
respective models.
