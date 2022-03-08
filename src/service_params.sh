# Update these values from "terraform output" of your service
# To get Jenkins URL IP, run following command on service admin VM:
# [opc@<mu-service>-admin ~]$ kubectl get svc -n wlsoke-ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o jsonpath='{.items[*].status.loadBalancer.ingress[0].ip}'
export BASTION_PUBLIC_IP=129.153.192.188
export ADMIN_PRIVATE_IP=10.0.2.4
export JENKINS_URL=http://10.0.6.9/jenkins

DIR=`dirname $0`
# WLS_OKE_SERVICE_SECRETS_FILE
source "DIR/../secrets/wlsoke_service_secrets.sh"
export SSH_PRIVATE_KEY_FILE=$DIR/ssh_key
echo "$SSH_PRIVATE_KEY" > $SSH_PRIVATE_KEY_FILE
chmod 600 $SSH_PRIVATE_KEY_FILE