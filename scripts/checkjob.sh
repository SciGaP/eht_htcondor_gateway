#!/bin/bash

# Check if the user provided an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <username>"
  exit 1
fi

folder="jobs"
jobname="*${1}*"
#echo $jobname

for subfolder in $(find "$folder" -type d -name "$jobname"); do
    # Do something with each subfolder
    outfolder="${subfolder}/job/out"
    h5count=$(find "$outfolder" -type f -iname "*.h5" | wc -l)
    jobid="${subfolder#*/}"
    echo $jobid:$h5count
    # You can add any other operations you'd like to perform on each subfolder here
done
