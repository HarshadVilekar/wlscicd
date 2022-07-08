#!/bin/bash

set -x

DIR=$WORKSPACE/src/wdtdemo
cd $DIR

# update properties file to use default cluster name for the domain
PROPS_FILE="$DIR/wls_deployment/src/domain/models/model.10.properties"
echo "cluster.name=${DOMAIN_NAME}-cluster" > $PROPS_FILE

# build wdt deployment files for the  app that we want to deploy
mvn install
exit_code=$?
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

LAUNCH="python3 $WORKSPACE/src/launch-jenkins-job.py"

# copy the payload files required for CI/CD Jenkins update_domain job to the admin vm @/u01/shared location
$LAUNCH scp_file_to_admin_vm $DIR/wls_deployment/src/domain/models/model.10.yaml /u01/shared/model.yaml
$LAUNCH scp_file_to_admin_vm $PROPS_FILE /u01/shared/model.properties
$LAUNCH scp_file_to_admin_vm $DIR/wls_deployment/target/wdt_archive.zip /u01/shared/archive.zip

# start the job on CI/CD Jenkins
$LAUNCH launch
exit_code=$?
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

# wait for the job completion
$LAUNCH wait_for_completion
exit_code=$?
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

# get the external lb URL for the app deployed by the update_domain job
APP_NAME="webapp"
$LAUNCH get_app_url $APP_NAME
