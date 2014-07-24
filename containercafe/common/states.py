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


class UnrecognizedState(Exception):
    pass


class State(object):
    INITIAL = 0
    CREATED = 1
    STARTED = 2
    RUNNING = 3
    STOPPED = 4
    DESTROYED = 5

    def __init__(self, initial_state=INITIAL):
        self.value = initial_state

    def __str__(self):
        return 'State({})'.format(self.value)

    def set_state(self, state):
        if hasattr(self, state):
            self.value = state
        else:
            raise UnrecognizedState
