"""
Copyright 2014 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import copy
import os
import shutil
import tempfile
from time import sleep

from containercafe.common.clients.base import BaseContainerClient
from containercafe.common.connectors.process \
    import _SIMPLE_SUCCESS_CMD_RESULT
from containercafe.common.states import State


class LXCError(Exception):
    pass


class LxcClient(BaseContainerClient):

    CREATE_CMD = 'lxc-create'
    START_CMD = 'lxc-start'
    EXECUTE_CMD = 'lxc-execute'
    WAIT_CMD = 'lxc-wait'
    STOP_CMD = 'lxc-stop'
    DESTROY_CMD = 'lxc-destroy'

    STOPPED = 'STOPPED'
    RUNNING = 'RUNNING'

    def __init__(self, name, preset_cfg=None, connection=None, clean=True):
        super(LxcClient, self).__init__(name=name, connection=connection)
        self._syscall_whitelist = list()
        self._config = self._init_config(preset_cfg)
        self._tmpdir_path = self._init_tmpdir()
        self.clean_container = clean

    def _run(self, cmd, prompt=None, timeout=None):
        """ Execute a specific command within the container. """

        # Target sets the style of connection (API, host, container)
        args = {'cmd': cmd}
        if prompt is not None:
            args['prompt'] = prompt
        if timeout is not None:
            args['timeout'] = int(timeout)

        try:
            output = self.connection.execute(**args)
        except Exception as err:
            raise err

        sleep(self.cmd_delay)
        return output

    def _check_state(self, *valid_states):
        if self._state.value not in valid_states:
            err_msg = 'LXC State {state} is not valid.'.format(
                state=self._state)
            raise LXCError(err_msg)

    def set_option(self, option, *values):
        self._config[option] = values

    def create(self):
        cmd = self.CREATE_CMD
        self._check_state(State.INITIAL)
        self._generate_rcfile()

        exec_target = '{cmd} -n {name} -f {rc_file}'.format(
            name=self.name, rc_file=self.rc_file, cmd=cmd)

        result = self._run(cmd=exec_target)
        if result.returncode == 0:
            self._requires_destroy = True
            self._state.set_state(State.CREATED)
        return result

    def start(self):
        cmd = self.START_CMD
        self._check_state(State.INITIAL, State.CREATED, State.STOPPED)
        self._generate_rcfile()

        exec_target = '{cmd} -n {name} -f {rc_file}'.format(
            name=self.name, rc_file=self.rc_file, cmd=cmd)

        result = self._run(cmd=exec_target)
        if result.returncode == 0:
            self._state.value = State.STARTED

        return result

    def execute(self, user_cmd, **kwargs):
        cmd = self.EXECUTE_CMD
        self._check_state(State.INITIAL, State.CREATED, State.STOPPED)
        self._generate_rcfile()

        # Format the actual command target
        exec_target = self._format_cmd(
            lxc_cmd=cmd, user_cmd=user_cmd, name=self.name,
            rc_file=self.rc_file)

        # Run the command and capture the result
        return self._run(cmd=exec_target, **kwargs)

    def wait(self, states):
        cmd = self.WAIT_CMD
        self._check_state(State.STARTED, State.RUNNING)

        exec_target = '{cmd} -n {name} -s {state}'.format(
            name=self.name, state=states, cmd=cmd)
        return self._run(cmd=exec_target)

    def stop(self):
        cmd = self.STOP_CMD
        self._check_state(State.STARTED, State.RUNNING)
        exec_target = '{cmd} -n {name}'.format(name=self.name, cmd=cmd)

        result = self._run(cmd=exec_target)
        if result.returncode == 0:
            self._state.value = State.STOPPED
        return result

    def destroy(self):
        cmd = self.DESTROY_CMD
        result = _SIMPLE_SUCCESS_CMD_RESULT

        # Only attempt a destroy if we really need to
        if self._requires_destroy:
            self._check_state(State.CREATED, State.STOPPED)
            exec_target = '{cmd} -n {name}'.format(name=self.name, cmd=cmd)

            result = self._run(cmd=exec_target)
            if result.returncode == 0:
                self._requires_destroy = False
                self._state.set_state(State.DESTROYED)
        return result

    def clean(self):
        if self.clean_container:
            self.destroy()
            if os.path.exists(self._tmpdir_path):
                shutil.rmtree(self._tmpdir_path)

    # LXC Container Specific Routines
    # ----------------------------------------------------
    def _init_config(self, preset_cfg):
        """ Initialize the configuration for LXC. """
        # Set our defaults
        config = dict({
            'lxc.utsname': self.name,
            'lxc.network.type': 'empty'})

        # Overwrite anything the user wants us to
        if preset_cfg is not None:
            config.update(preset_cfg)
        return config

    def _init_tmpdir(self):
        """ Setup the temp directory for storing local config files. """
        return tempfile.mkdtemp(
            prefix='{}.'.format(self.name), suffix='.lxc-sectest')

    @classmethod
    def _format_cmd(cls, lxc_cmd, user_cmd, name, rc_file=None):
        return '{lxc_cmd} -n {name} -f {rc_file} -- {user_cmd}'.format(
            lxc_cmd=lxc_cmd, name=name, rc_file=rc_file, user_cmd=user_cmd)

    def _generate_rcfile(self):
        # Is there a config already? Yeah? Blast it.
        if self.rc_file is not None and os.path.exists(self.rc_file):
            os.remove(self.rc_file)

        # Make a shallow copy to set our built in command params
        actual_cfg = copy.copy(self._config)

        # Set seccomp cfg var if there are values in the syscall whitelist
        if len(self._syscall_whitelist) > 0:
            actual_cfg['lxc.seccomp'] = self._write_seccomp_policy(
                self._tmpdir_path, self._syscall_whitelist)

        # Write the LXC configuration (writes locally)
        self.rc_file = self.write_cfg(self._tmpdir_path, actual_cfg)

        # Write file remotely
        cfg_file = self.get_cfg(self.rc_file)
        self.connection.execute('mkdir -p {temp_dir}'.format(
            temp_dir=self._tmpdir_path))
        self.connection.execute('echo "{cfg_file}" >> {remote_file}'.format(
            cfg_file=cfg_file, remote_file=self.rc_file))

    def _show_rcfiles(self):
        rc_files = ''
        for root, dirs, files in os.walk(self._tmpdir_path):
            for name in files:
                with open(os.path.join(root, name), 'r') as rc_file:
                    rc_files = ('{output}LXC {name}:\n{content}'.format(
                        output=rc_files, name=name, content=rc_file.read()))
        return rc_files

    @classmethod
    def _write_seccomp_policy(cls, path, syscall_whitelist,
                              filename='syscall_whitelist'):
        whitelist_file = os.path.join(path, filename)
        with open(whitelist_file, 'w') as cfg_out:
            cfg_out.write('1\nwhitelist\n0\n')
            for syscall in syscall_whitelist:
                cfg_out.write('{sys_call}\n'.format(sys_call=syscall))
        return whitelist_file
