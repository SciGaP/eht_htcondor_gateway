#!/bin/bash

# submit job by a given experimentid
# create the subfolder under jobs
# copy job_template to jobs/experimentid
# check if experiment_BATCH.ALL exists in staging folder
# copy this BATCH.ALL to replace BATCH.ALL in the job template folder
# submit the job if runs on eht node

# Check if the user provided an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <experiment_id>"
  exit 1
fi

# Create the directory
mkdir -p jobs/"$1"

# cp job template folder
cp -pr job_template jobs/"$1"/job

# check if BATCH exists under staging 
batchfile="staging/${1}_BATCH.ALL"

if [[ -f "$batchfile" ]]; then
	echo "$batchfile is found, copy to job folder"
	cp "$batchfile" jobs/"$1"/job/par/BATCH.ALL
else
	echo "$batchfile is not found, use the default one"
fi

cd jobs/"$1"/job

# modify submit script
# in bin/submit, replace batch_name = as batch_name = $1

new_var="\"$1\""
#echo "$new_var"

# use double quote for variable
sed -i "s/batch_name =/batch_name = $new_var/g" bin/submit

hostname=$(hostname)
echo "$hostname"

# submit job
if [[ "$hostname" == "ospool-eht2000" ]]; then
	echo "running the submit command ..."
	bin/batches
else
	echo "not on the eht node!"
fi 
