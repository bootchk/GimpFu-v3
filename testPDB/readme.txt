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

The PDB may change often (with any commit) so you may need to do the following frequently:

Process:

1) call pdb.dump_to_file(f) to generate pdb.txt.  Use plugin dump_pdb.py  in GUI Test>Dump PDB...

2) generate json.   >nawk -f parsePDBTxt.nawk pdb.txt > pdb.json

3) edit pdb.json to remove the last comma

3) run the test plugin    Test>MegaTestGimp  which reads the .json
