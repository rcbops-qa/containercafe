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

import subprocess


class CommandResult(object):

    def __init__(self, returncode, output):
        self.returncode = returncode
        self.output = output

    def __str__(self):
        return str(self.to_dict)

    @property
    def to_dict(self):
        return {"returncode": self.returncode,
                "output": self.output}

    @property
    def _output(self):
        return self.output.replace('\n', '')

    @property
    def _content(self):
        return self.output

_SIMPLE_SUCCESS_CMD_RESULT = CommandResult(0, '')


class CommandError(Exception):
    def __init__(self, result, *args, **kwargs):
        super(CommandError, self).__init__(args, kwargs)
        self.result = result


class Command(object):

    @classmethod
    def run_command(cls, cmd, cwd=None, env=None):
        output = bytearray()
        proc = subprocess.Popen(cmd, cwd=cwd, shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                env=env, close_fds=True)

        while proc.poll() is None:
            line = proc.stdout.readline()
            if line is None:
                break
            output.extend(line)

        result = CommandResult(proc.returncode, output)
        if result.returncode and result.returncode != 0:
            raise CommandError(result)

        return result
