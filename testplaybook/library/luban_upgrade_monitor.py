from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '2.0',
                    'status': ['dev'],
                    'supported_by': 'luban'}

DOCUMENTATION = '''
---
module: async_log
short_description: Obtain log from file of asynchronous task
'''

import json
import os
import pickle
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from kubernetes import client,watch,config
class AsyncLogHelper(object):
    # line_terminators = ('\r\n', '\n', '\r')
    def __init__(self, logfile):
        self.seek_pos = 0
        self.logfile = logfile
        self.remaining = ""

    def get_log(self):
        if not os.path.exists(self.logfile) or not os.path.isfile(self.logfile):
            return []
        with open(self.logfile) as f:
            f.seek(self.seek_pos)
            lines = f.readlines()
            self.seek_pos = f.tell()
            if not lines:
                return []
            if len(self.remaining):
                lines[0] = self.remaining+lines[0]
            if '\n' in lines[-1]:
                return lines[:]
            else:
                self.remaining = lines[-1]
                return lines[:-1]
#

class Cell(object):
    def __init__(self):
        self.status = ""
        self.name = ""


def main():
    config_path = "/Users/xliuxu/.bluemix/plugins/container-service/clusters/sps-preprod/kube-config-dal12-sps-preprod.yml"
    config_path = "/Users/xuliuxl/.bluemix/plugins/container-service/clusters/xuliuxl-vpn-test-1/kube-config-dal12-xuliuxl-vpn-test-1.yml"
    try:
        config.load_kube_config(config_path)
    except (IOError, config.ConfigException):
        # If we failed to load the default config file then we'll return
        # an empty configuration
        # If one was specified, we will crash
        if not config:
            config.load_incluster_config()
        raise
    apps_api = client.AppsV1Api()
    core_api = client.CoreV1Api()
    # ret = v1.read_namespaced_pod_status('public-cr7952881a96e14eb69a9e7d7654c8270b-alb1-65f956c88c-7vdbb','kube-system')
    # print(ret.status.phase)
    sts = apps_api.read_namespaced_stateful_set_status('web','default')

    print(sts)
    print("replica: %d" % sts.spec.replicas)
    # print(sts.status.current_revision)
    sts_revision = sts.status.current_revision
    print("revision: %s" % sts.status.current_revision )
    for i in range(sts.spec.replicas):
        pod = core_api.read_namespaced_pod("web-%d" % i,'default')
        # print(pod)
        current_revision = pod.metadata.labels["controller-revision-hash"]
        if current_revision != sts_revision:
            print("NotUpgraded")
        else:
            print("Upgrading")

if __name__ == '__main__':
    main()
