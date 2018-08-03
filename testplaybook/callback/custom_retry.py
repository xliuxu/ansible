# (c) 2015, Andrew Gaffney <andrew@agaffney.org>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: actionable
    type: stdout
    short_description: shows only items that need attention
    description:
      - Use this callback when you dont care about OK nor Skipped.
      - This callback suppreses any non Failed or Changed status.
    version_added: "2.1"
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout callback in configuration
'''

from ansible.plugins.callback.default import CallbackModule as CallbackModule_default
from ansible import constants as C


class CallbackModule(CallbackModule_default):

    CALLBACK_VERSION = 2.3
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'custom_retry'

    def __init__(self):
        self.super_ref = super(CallbackModule, self)
        self.super_ref.__init__()
        self.last_task = None
        self.shown_title = False

    def v2_runner_retry(self, result):
        if 'tag' in result._result:
            if not result._result['tail_log']:
                return
            tag_prefix = "LOG [%s] " % result._result['tag']
            msg = tag_prefix + tag_prefix.join(result._result['tail_log'])
            self._display.display(msg, color=C.COLOR_DEBUG)
        else:
            self.super_ref.v2_runner_retry(result)

