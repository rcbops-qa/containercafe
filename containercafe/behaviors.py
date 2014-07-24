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


class ContainerBehavior(object):

    def __init__(self, container_type):
        self.container_type = container_type

    def __enter__(self):
        self.container_type.create()
        self.container_type.wait(self.container_type.STOPPED)
        self.container_type.start()
        self.container_type.wait(self.container_type.RUNNING)
        return self.container_type

    def __exit__(self, container_type):
        if container_type is not None:
            pass

        self.container_type.stop()
        self.container_type.wait(self.container_type.STOPPED)
        self.container_type.destroy()
        self.container_type.clean()

    @property
    def get_context(self):
        return self.container_type
