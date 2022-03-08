import os
import sys


class CicdRestExecutor:
    def __init__(self, ssh_key, bastion_ip, admin_ip, jenkins_url, jenkins_creds):
        self.jenkins_url = jenkins_url
        self.jenkins_creds = jenkins_creds
        ssh_flags="-o LogLevel=quiet -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
        proxy_command = "ssh -W %h:%p -i {0} opc@{1}".format(self.ssh_key, self.bastion_ip)
        self.ssh_admin_command='ssh -i {0} {1} -o ProxyCommand="{2}" opc@{3}'.format(self.ssh_key, ssh_flags, proxy_command, admin_ip)

    def get_rest_command(self, command):
        rest_command="curl -u {1} {2} {3}".format(self.jenkins_creds, self.jenkins_url, command)
        return '{0} "{1}"'.format(self.ssh_admin_command, rest_command)

    # Returns process execution results (stdout+stderr and return value) when the process exits.
    # Waits for the process completion. There is no polling, no timeout.
    # Logs stderr generated by the process.
    def execute_rest_api(self, rest_api):
        command = self.get_rest_command(rest_api)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        exit_status = process.returncode
        if err:
            self.logger.info(err.strip())
        return out, exit_status


def validate_jenkins_job_is_present(cicd_rest_executor, job_name):
    rest_api = '/api/json?pretty=true'
    cmdout = cicd_rest_executor.execute_rest_api(rest_api)
    expected_string = cicd_rest_executor.jenkins_url + "/job/" + job_name + "/"
    if expected_string not in str(cmdout):
        print("ERROR: validate_jenkins_job_is_present: job " + job_name + " not found !")
        return False
    print("PASS: validate_jenkins_job_is_present: " + job_name)
    return True

def exit_with_error(msg):
    print ("Error: " + msg)
    sys.exit(1)


def pipeline_validation():
    if len(sys.argv) <= 4:
        exit_with_error("missing required arguments: bastion_ip admin_ip jenkins_url ssh_private_key_file")

    bastion_ip = sys.argv[1]
    admin_ip = sys.argv[2]
    jenkins_url = sys.argv[3]
    ssh_private_key_file = sys.argv[4]
    jenkins_creds = os.environ['JENKINS_CREDS']
    if not jenkins_creds:
        exit_with_error("Environment variable JENKINS_CREDS not defined!")

    cicd_rest_executor = CicdRestExecutor(ssh_private_key_file, bastion_ip, admin_ip, jenkins_url, jenkins_creds)

    try:
        validation_ok = validate_jenkins_job_is_present(cicd_rest_executor)

        if validation_ok:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        exit_with_error(str(e))


if __name__ == '__main__':
    pipeline_validation()
