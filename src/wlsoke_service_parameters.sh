# Update these values from "terraform output" command for your service, after the service is created.
# To get Jenkins URL IP, run the following command on service admin VM:
# [opc@<my-service>-admin ~]$ kubectl get svc -n wlsoke-ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o jsonpath='{.items[*].status.loadBalancer.ingress[0].ip}'
export BASTION_PUBLIC_IP=xx.xx.xx.xx
export ADMIN_PRIVATE_IP=yy.yy.yy.yy
export JENKINS_URL=http://zz.zz.zz.zz/jenkins
# username:password credentials for WLS-OKE Jenkins.
export JENKINS_CREDS="your_jenkins_service_username:your_jenkins_service_password"
# your ssh private key pair for the ssh public key that was used to create wls-oke service
export SSH_PRIVATE_KEY=\
"-----BEGIN RSA PRIVATE KEY-----
add your multi-line
ssh key here
-----END RSA PRIVATE KEY-----"
