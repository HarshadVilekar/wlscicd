export ADMIN_IP="x.x.x.x"
export BASTION_IP="y.y.y.y"
export SSH_PRIVATE_KEY_FILE="<full_path_to_ssh_private_key_file_accessible_from_jenkins_build_executor_agent>"
export JENKINS_CREDS="weblogic:welcome1"
export JENKINS_JOB_NAME="DeploySampleApp"
# create token under the menu: Job Configuration - Build Trigger - Authentication Token to trigger builds remotely
export JENKINS_JOB_TOKEN_NAME="helloToken"
