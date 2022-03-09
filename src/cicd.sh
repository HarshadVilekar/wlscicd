# full path to ssh private key file. This file is created here.
DIR=`dirname $0`
source $DIR/service_params.sh
CMD="python $DIR/cicd.py $BASTION_PUBLIC_IP $ADMIN_PRIVATE_IP $JENKINS_URL $SSH_KEY_FILE"
echo $CMD
$CMD