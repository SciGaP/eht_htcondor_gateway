# ipole-osg

A simple setup for running a large number of `ipole` jobs on the Open
Science Grid (OSG) using HTCondor.

## Usage

This git repository is designed to be cloned to OSG connect as a run
directory for both submitting a large OSG job and gathering the
output.
To start,

    ssh osg # OSG now requires two-factor authentication
    cd ~/runs
    git clone git@github.com:bhpire/ipole-osg.git Ma+0.94_w5_230GHz
    cd Ma+0.94_w5_230GHz

All the scripts are placed inside `bin/`.
The empty directories `log/`, `out/`, and `par/` will be used to stage
OSG run logs, `ipole` output, and parameter files.

Before submitting a job, one needs to copy a static linked `ipole`
binary to `bin/`.

    cp ~/src/ipole/ipole bin
    md5sum bin/ipole
    vi bin/wrapper # update $ipmd5 with the new md5

Edits may be made to `bin/pargen` to generate the necessary parameter
sets.
Then, simply submit an OSG job by

    bin/batch

`bin/batch` uses `bin/pargen` to generate a list of parameter sets
based on all the GRMHD input data and the parameter listed inside
`bin/pargen`.
The actual job submission is done by `bin/submit`, whic is a standard
Condor submission script starts with a hashbang directive to use the
system `condor_submit`.
These parameter sets are then passed to `bin/wrapper` on the worker
machines as command line arguments.
`bin/wrapper` will automatically generate a `ipole` parameter file
based on the arguments, and start `ipole` with it.

All Condor logs, `stdout`, and `stderr` will be sent to `log/`.
The parameter files and spectrum output will be saved to `out/`.
Their file names are transform according to the rules described in
`bin/submit`.

# Demo

Useful commands during demo:

    # Compile ipole
    ssh osg # OSG now requires two-factor authentication
    cd ~/src
    git clone https://github.com/AFD-Illinois/ipole.git ipole-demo
    cp /ipole-demo
    vi makefile # enable static linkage
    module load gsl hdf5
    make
    nm ipole | grep ' U ' # there should not be any undefined symbols

    # Clone the ipole-osg tools and use it
    cd ~/runs
    git clone git@github.com:bhpire/ipole-osg.git Ma+0.94_w5_230GHz
    cd Ma+0.94_w5_230GHz
    cp ~/src/ipole-demo/ipole bin/
    md5sum bin/ipole
    vi bin/wrapper # update $ipmd5 with the new md5
    bin/batch # ctrl-C to submit part of the jobs
    condor_q
    condor_q -run
    condor_q -long JOB_ID
