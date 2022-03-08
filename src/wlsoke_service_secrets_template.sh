# Update this file and copy to the location defined by the line with the comment WLS_OKE_SERVICE_SECRETS_FILE
# username:password credentials for WLS-OKE Jenkins.
export JENKINS_CREDS="your_jenkins_service_username:your_jenkins_service_password"
# your ssh private key pair for the ssh public key that was used to create wls-oke service
export SSH_PRIVATE_KEY=\
"-----BEGIN RSA PRIVATE KEY-----
add your multi line ssh key string here
-----END RSA PRIVATE KEY-----"
