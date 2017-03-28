import os
from collections import namedtuple
from ansible import constants as C
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.utils.vars import (
    load_extra_vars,
    load_options_vars,
)
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class Playbook(object):

    option_fields = [
            'ask_pass',
            'ask_vault_pass',
            'become',
            'become_method',
            'become_user',
            'check',
            'connection',
            'diff',
            'extra_vars',
            'flush_cache',
            'force_handlers',
            'forks',
            'listhosts',
            'listtasks',
            'listtags',
            'inventory',
            'module_path',
            'new_vault_password_file',
            'output_file',
            'private_key_file',
            'remote_user',
            'scp_extra_args',
            'sftp_common_args',
            'skip_tags',
            'ssh_common_args',
            'ssh_extra_args',
            'su',
            'subset',
            'su_user',
            'sudo',
            'sudo_user',
            'syntax',
            'tags',
            'timeout',
            'vault_password_file',
            # Not working atm. Not sure why.
            'verbosity',
            ]

    def __init__(self,
            options={},
            playbooks=[],
            loader=DataLoader(),
            result_callback=None,
            passwords=None,
            inventory=None):
        self._Options = namedtuple('Options', self.option_fields)
        self._options = None
        self.set_options(**options)

        if ((self._options.su or self._options.su_user) and
            (self._options.sudo or self._options.sudo_user) or
            (self._options.su or self._options.su_user) and
            (self._options.become or self._options.become_user) or
            (self._options.sudo or self._options.sudo_user) and
            (self._options.become or self._options.become_user)):

            raise Exception(
                "Sudo options ('sudo', 'sudo_user', and 'ask_sudo_pass') "
                "and su options ('su', 'su_user', and 'ask_su_pass') "
                "and become options ('become', 'become_user', and 'ask_become_pass')"
                " are exclusive of each other"
            )

        if (self._options.ask_vault_pass and self._options.vault_password_file):
            raise Exception(
                "'ask_vault_pass' and 'vault_password_file' are mutually exclusive"
            )

        if self._options.forks < 1:
            raise Exception('The number of processes (--forks) must be >= 1')

        display.verbosity = self._options.verbosity
        self._loader = loader
        self._variable_manager = VariableManager()
        self._variable_manager.extra_vars = load_extra_vars(
                loader=self._loader, options=self._options)
        print(self._variable_manager.extra_vars)
        self._variable_manager.option_vars = load_options_vars(self._options)
        self._result_callback = result_callback
        self._inventory = inventory
        self._passwords = passwords

        self._playbooks = []
        for pb in playbooks:
            if os.path.isabs(pb):
                self._playbooks.append(pb)
            else:
                pbdir = os.path.dirname(__file__)
                self._playbooks.append(os.path.join(pbdir, pb))

        if inventory is None:
            self._inventory = Inventory(
                loader=self._loader,
                variable_manager=self._variable_manager,
                host_list=self._options.inventory)

        self._pbex = PlaybookExecutor(
                playbooks=self._playbooks,
                inventory=self._inventory,
                variable_manager=self._variable_manager,
                loader=self._loader,
                options=self._options,
                passwords=self._passwords)


    def play(self):
        self._pbex.run()


    def set_options(self, **kw):
        if self._options is None:
            options = {
                'ask_pass': C.DEFAULT_ASK_PASS,
                'ask_vault_pass': C.DEFAULT_ASK_VAULT_PASS,
                'become': C.DEFAULT_BECOME,
                'become_method': C.DEFAULT_BECOME_METHOD,
                'become_user': C.DEFAULT_BECOME_USER,
                'check': False,
                'connection': C.DEFAULT_TRANSPORT,
                'diff': False,
                'extra_vars': [],
                'forks': C.DEFAULT_FORKS,
                'force_handlers': C.DEFAULT_FORCE_HANDLERS,
                'inventory': C.DEFAULT_HOST_LIST,
                'module_path': C.DEFAULT_MODULE_PATH,
                'private_key_file': C.DEFAULT_PRIVATE_KEY_FILE,
                'remote_user': C.DEFAULT_REMOTE_USER,
                'scp_extra_args': '',
                'sftp_common_args': '',
                'ssh_common_args': '',
                'ssh_extra_args': '',
                'su': C.DEFAULT_SU,
                'subset': C.DEFAULT_SUBSET,
                'sudo': C.DEFAULT_SUDO,
                'syntax': False,
                'tags': 'all',
                'timeout': C.DEFAULT_TIMEOUT,
                'vault_password_file': C.DEFAULT_VAULT_PASSWORD_FILE,
                # Changed to C.DEFAULT_VERBOSITY in 2.3
                'verbosity': 0,
            }
            options.update(kw)
            for k in self.option_fields:
                if k not in options:
                    options[k] = None

            self._options = self._Options(**options)
            return self._options

        self._options._replace(**kw)
        return self._options
