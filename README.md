# YCRC Test Suite

A set of python unit tests to check for a good environment on the YCRC Clusters.

Current list of tests and what they do:

- Quota: checks that you aren't over quota
- SSH: checks for proper permissions and a valid passwordless private key
- Lmod: makes sure that Lmod is available and `StdEnv` is loaded
- Slurm: makes sure that running `squeue` works and that valid slurm accounts exist for user
