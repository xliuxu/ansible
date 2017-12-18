# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: default
    type: stdout
    short_description: default Ansible screen output
    version_added: historical
    description:
        - This is the default output callback for ansible-playbook.
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout in configuration
'''

from ansible import constants as C
from ansible.plugins.callback import CallbackBase

import json

class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 0.1
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'custom_retry'

    def __init__(self):

        self._play = None
        self._last_task_banner = None
        super(CallbackModule, self).__init__()


    def v2_runner_retry(self, result):
        if 'tag' in result._result:
            if not result._result['tail_log']:
                return
            tag_prefix = "LOG [%s] " % result._result['tag']
            msg = tag_prefix + tag_prefix.join(result._result['tail_log'])
        self._display.display(msg, color=C.COLOR_DEBUG)

