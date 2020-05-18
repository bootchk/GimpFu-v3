This directory contains a nawk script to convert a pdb dump (pdb.txt) to json (pdb.json).
And examples of said data files, which should be refreshed as gimp repository changes.

pdb.json is used as the input to plug-ins/megaTestGimp.
megaTestGimp is data-driven (pdb.json), automated test of PDB.
For now the tests are fuzzy,
i.e. with type valid but arbitrarily valued inputs to procedures under test,
only testing for crashes, with a human inspecting the results.
In the future, the testing could be expanded to
test even more randomly,
with values that might test edge cases, e.g. zeros.
