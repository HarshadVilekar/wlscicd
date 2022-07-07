DIR=$WORKSPACE/src/wdtdemo
cd $DIR
PROPS_FILE="$DIR/wls_deployment/src/domain/models/model.10.properties"
echo "cluster.name=${DOMAIN_NAME}-cluster" > $PROPS_FILE
mvn install
LAUNCH="python3 $WORKSPACE/src/launch-jenkins-job.py"

#scp update_domain payload files to admin vm @/u01/shared: ./wls_deployment/src/domain/models/model.10.yaml,model.10.properties, ./wls_deployment/target/wdt_archive.zip
$LAUNCH scp_file_to_admin_vm $DIR/wls_deployment/src/domain/models/model.10.yaml /u01/shared/model.yaml
$LAUNCH scp_file_to_admin_vm $DIR/wls_deployment/src/domain/models/model.10.properties /u01/shared/model.properties
$LAUNCH scp_file_to_admin_vm $DIR/wls_deployment/target/wdt_archive.zip /u01/shared/archive.zip

$LAUNCH launch
$LAUNCH wait_for_completion

