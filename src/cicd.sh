# full path to ssh private key file. This file is created here.
DIR=`dirname $0`
source $DIR/service_params.sh
python $DIR/cicd.py $BASTION_PUBLIC_IP $ADMIN_PRIVATE_IP $JENKINS_URL $SSH_PRIVATE_KEY_FILE