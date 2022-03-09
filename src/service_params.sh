DIR=`dirname $0`
# This file is copied over by the CI/CD job, and sets following parameters:
# BASTION_PUBLIC_IP, ADMIN_PRIVATE_IP, JENKINS_URL, JENKINS_CREDS, SSH_KEY
source "$DIR/wlsoke_service_parameters.sh"
export SSH_KEY_FILE=$DIR/ssh_key
echo "$SSH_KEY" > $SSH_KEY_FILE
chmod 600 $SSH_KEY_FILE