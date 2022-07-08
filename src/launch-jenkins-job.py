from subprocess import check_output, STDOUT, CalledProcessError
import os
import sys
import json
import time

# Execute specified Jenkins Build on WLS-OKE CI/CD Jenkins setup
# Set following environment variables before running this script:
#   For WLS-OKE Stack: basion public ip, admin private ip, SSH private key for Admin VM instance
#   For WLS-OKE CI/CD Jenkins: Jenkins Credential, Jenkins job to be executed, remote access token for the Jenkins job
class JenkinsBuild:

    def __init__(self):
        self.get_env_vars()
        self.jenkins_url = self.get_jenkins_url()
        self.jenkins_creds_command = "--user {0}".format(self.jenkins_creds)
        self.curl_command = "curl --silent -X GET"
        crumb = self.get_jenkins_crumb()
        self.jenkins_crumb_header = "-H Jenkins-Crumb:{0}".format(crumb)
        self.jenkins_build_with_parameters = "buildWithParameters?token={0}".format(self.jenkins_job_token_name)

    def get_update_domain_job_params(self):
        shared_file_system = "Shared%20File%20System"
        shared_location = "%2Fu01%2Fshared%2F"
        domain_name_params = "&Domain_Name={0}".format(self.domain_name)
        archive_params = "&Archive_Source={0}&Archive_File_Location={1}archive.zip".format(shared_file_system, shared_location)
        domain_model_source_params = "&Domain_Model_Source={0}&Model_File_Location={1}model.yaml".format(shared_file_system, shared_location)
        variable_source_params = "&Variable_Source={0}&Variable_File_Location={1}model.properties".format(shared_file_system, shared_location)
        rollback_params = "&Rollback_On_Failure=true"
        return domain_name_params + archive_params + domain_model_source_params + variable_source_params + rollback_params

    def missing_environment_variable(self, env_var_name):
        print("set environmanet variable {0} and try again".format(env_var_name))
        sys.exit(1)

    def get_env_vars(self):
        self.ssh_private_key_file=os.getenv('SSH_PRIVATE_KEY_FILE')
        self.bastion_ip=os.getenv('BASTION_IP')
        self.admin_ip=os.getenv('ADMIN_IP')
        self.jenkins_creds=os.getenv('JENKINS_CREDS')
        self.jenkins_job_name = os.getenv('JENKINS_JOB_NAME')
        self.domain_name = os.getenv('DOMAIN_NAME')
        # token is created at the menu:
        # Job Configuration - Build Trigger - Authentication Token to trigger builds remotely
        self.jenkins_job_token_name = os.getenv('JENKINS_JOB_TOKEN_NAME')

        if not self.ssh_private_key_file:
            self.missing_environment_variable("SSH_PRIVATE_KEY_FILE")

        if not self.bastion_ip:
            self.missing_environment_variable("BASTION_IP")

        if not self.admin_ip:
            self.missing_environment_variable("ADMIN_IP")

        if not self.jenkins_creds:
            self.missing_environment_variable("JENKINS_CREDS")

        if not self.jenkins_job_name:
            self.missing_environment_variable("JENKINS_JOB_NAME")

        if not self.jenkins_job_token_name:
            self.missing_environment_variable("JENKINS_JOB_TOKEN_NAME")

        if not self.domain_name:
            self.missing_environment_variable("DOMAIN_NAME")

        ssh_option_quiet = '-o LogLevel=quiet'
        self.ssh_options = ssh_option_quiet + ' -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {0} -o ProxyCommand="ssh -W %h:%p -i {0} opc@{1}"'.format \
            (self.ssh_private_key_file, self.bastion_ip)

    def scp_file_to_admin_vm(self, source_file_path, dest_file_path):
        scp_to_admin_vm_cmd='scp {0} {1} opc@{2}:{3}'.format(self.ssh_options, source_file_path, self.admin_ip, dest_file_path)
        msg = "{0} --> admin_vm:{1}".format(source_file_path, dest_file_path)
        cmd_output, status = self.execute_command(scp_to_admin_vm_cmd, output_expected=False, print_command=False)
        if status:
            print("OK: {0}".format(msg))
        else:
            print("ERROR: {0} [status={1}][{2}]".format(msg, status, cmd_output))

    def execute_shell_command_on_admin_vm(self, command, output_expected=True, print_output=False, print_command=False):
        ssh_admin_vm_cmd = 'ssh {0} opc@{1}'.format(self.ssh_options, self.admin_ip)
        shell_command = "{0} '{1}'".format(ssh_admin_vm_cmd, command)
        return self.execute_command(shell_command, output_expected=output_expected, print_output=print_output, print_command=print_command)

    def execute_command(self, command, output_expected=True, print_output=False, print_command=False):
        cmd_output = ""
        if print_command:
            print(command)
        try:
            cmd_output = check_output(command, shell=True, stderr=STDOUT, universal_newlines=True).rstrip('\n')
        except CalledProcessError as cmd_exec_exception:
            print("ERROR: {0} returned status {1} [{2}]".format(command, cmd_exec_exception.returncode, cmd_exec_exception.output))
            status = False
            return cmd_output, status
        if output_expected and not cmd_output:
            print("Unable to get output of command [{0}]".format(command))
            status = False
        elif not output_expected and cmd_output:
            print("Unexpected output [{0}] returned by command [{1}]".format(cmd_output, command))
            status = False
        else:
            status = True
            if print_output:
                print(cmd_output)

        return cmd_output, status

    def get_jenkins_url(self):
        get_internal_lb_ip_cmd = 'kubectl get svc -n wlsoke-ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o jsonpath="{.items[*].status.loadBalancer.ingress[0].ip}"'
        internal_lb_ip, status = self.execute_shell_command_on_admin_vm(get_internal_lb_ip_cmd)
        return "http://{0}/jenkins/".format(internal_lb_ip)

    def get_jenkins_crumb(self):
        crumb_url = self.jenkins_url+"crumbIssuer/api/json"
        get_crumb_command = "{0} {1} {2}".format(self.curl_command, crumb_url, self.jenkins_creds_command)
        jenkins_crumb, status = self.execute_shell_command_on_admin_vm(get_crumb_command)
        #{"_class":"hudson.security.csrf.DefaultCrumbIssuer","crumb":"aaab9fba5d3eb9cf375d18f9a2e7ff6be730ea82210f9feb54b12d53fc91a4fe","crumbRequestField":"Jenkins-Crumb"}
        jenkins_crumb_json = json.loads(jenkins_crumb)
        return jenkins_crumb_json["crumb"]

    def launch(self):
        #example: curl  -X GET  http://10.0.6.9/jenkins/job/HelloWorld/build?token=helloToken -d "{}" --user USR:PWD  -H 'Jenkins-Crumb: 6e825b6ab72af4a8456c5bbcd610e1d23a022ddbefcea788488c1de04e2e3a95'
        build_launch_command = self.get_update_domain_job_launch_command() if self.jenkins_job_name == "update%20domain" else self.get_job_launch_command()
        output, status = self.execute_shell_command_on_admin_vm(build_launch_command, output_expected=False, print_command=True)
        if not status:
            print("Unable to start the job {0}".format(self.jenkins_job_name))
        else:
            print("Started the job {0}".format(self.jenkins_job_name))
        return status

    def get_job_launch_command(self):
        return '{0} "{1}job/{2}/build?token={3}" {4} {5}'.format(
            self.curl_command, self.jenkins_url, self.jenkins_job_name, self.jenkins_job_token_name, self.jenkins_creds_command, self.jenkins_crumb_header)

    def get_update_domain_job_launch_command(self):
        return '{0} {5} {6} "{1}job/{2}/{3}{4}"'.format(
            self.curl_command, self.jenkins_url, self.jenkins_job_name, self.jenkins_build_with_parameters, self.get_update_domain_job_params(), self.jenkins_creds_command, self.jenkins_crumb_header)

    def wait_for_completion(self):
        build_status_command = "{0} {1}job/{2}/lastBuild/api/json {3}".format(
            self.curl_command, self.jenkins_url, self.jenkins_job_name, self.jenkins_creds_command)
        completed = False
        success = False
        time.sleep(10)
        while not completed:
            build_status_output, status = self.execute_shell_command_on_admin_vm(build_status_command, print_output=False)
            build_status_output_json = json.loads(build_status_output)
            # this field returns "true" as long as the build is running
            if not build_status_output_json["building"]:
                success = build_status_output_json["result"] and build_status_output_json["result"] == "SUCCESS"
                completed = True
            print(".")
            time.sleep(30)

        print ("Jenkins CI/CD Job {0} Build {1} status: {2}".format(self.jenkins_job_name, build_status_output_json["number"], build_status_output_json["result"]))
        return success


if __name__ == '__main__':
    usage_message = "Usage: launch-jenkins-job.py [launch | wait_for_completion | scp_file_to_admin_vm]"
    if len(sys.argv) < 2:
        print(usage_message)
        sys.exit(1)
    operation = sys.argv[1]
    jenkins_build = JenkinsBuild()
    if operation == "launch":
        if not jenkins_build.launch():
            sys.exit(1)
    elif operation == "wait_for_completion":
        if not jenkins_build.wait_for_completion():
            sys.exit(1)
    elif operation == "scp_file_to_admin_vm":
        if len(sys.argv) < 4:
            print("Usage: launch-jenkins-job.py scp_file_to_admin_vm <source_file_path> <dest_file_path>")
            sys.exit(1)
        src_file_path = sys.argv[2]
        dest_file_path = sys.argv[3]
        if not jenkins_build.scp_file_to_admin_vm(src_file_path, dest_file_path):
            sys.exit(1)
    else:
        print(usage_message)
        sys.exit(1)
    sys.exit(0)
