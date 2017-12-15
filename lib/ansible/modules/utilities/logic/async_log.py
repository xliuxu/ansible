#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>, and others
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}


DOCUMENTATION = '''
---
module: async_status
short_description: Obtain status of asynchronous task
description:
     - This module gets the status of an asynchronous task.
     - This module is also supported for Windows targets.
version_added: "0.5"
options:
  jid:
    description:
      - Job or task identifier
    required: true
  mode:
    description:
      - if C(status), obtain the status; if C(cleanup), clean up the async job cache
        located in C(~/.ansible_async/) for the specified job I(jid).
    choices: [ "status", "cleanup" ]
    default: "status"
notes:
    - See also U(http://docs.ansible.com/playbooks_async.html)
    - This module is also supported for Windows targets.
author:
    - "Ansible Core Team"
    - "Michael DeHaan"
'''

import json
import os
import pickle
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems


class AsyncLogHelper(object):
    # line_terminators = ('\r\n', '\n', '\r')
    def __init__(self, logfile):
        self.seek_pos = 0
        self.logfile = logfile
        self.remaining = ""

    def get_log(self):
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

def main():

    module = AnsibleModule(argument_spec=dict(
        jid=dict(required=True),
        tail_file=dict(required=True)
    ))

    jid = module.params['jid']
    tail_file = module.params['tail_file']

    # setup logging directory
    logdir = os.path.expanduser("~/.ansible_async")
    log_path = os.path.join(logdir, jid)
    async_log_status = os.path.join(logdir, jid+"_async_log_status")
    if not os.path.exists(log_path):
        module.fail_json(msg="could not find job", ansible_job_id=jid, started=1, finished=1)

    data = None
    try:
        data = open(log_path).read()
        data = json.loads(data)
    except Exception:
        if not data:
            # file not written yet?  That means it is running
            module.exit_json(results_file=log_path, ansible_job_id=jid, started=1, finished=0 )
        else:
            module.fail_json(ansible_job_id=jid, results_file=log_path,
                             msg="Could not parse job output: %s" % data, started=1, finished=1 )
    if os.path.exists(async_log_status):
        async_log_helper = pickle.loads(open(async_log_status))
    else:
        async_log_helper = AsyncLogHelper(tail_file)

    data['tail_log'] = async_log_helper.get_log()
    if 'started' not in data:
        data['finished'] = 1
        data['ansible_job_id'] = jid
    elif 'finished' not in data:
        data['finished'] = 0
    # with open(async_log_status,'wb') as f:
    #     pickle.dump(async_log_helper,f)
    # Fix error: TypeError: exit_json() keywords must be strings
    data = dict([(str(k), v) for k, v in iteritems(data)])
    module.exit_json(**data)


if __name__ == '__main__':
    main()
