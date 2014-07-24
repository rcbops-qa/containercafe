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

from cloudcafe.common.models.configuration import ConfigSectionInterface


class ContainersSetupConfig(ConfigSectionInterface):
    """ Basic Container Setup Information """
    SECTION_NAME = 'containers'

    @property
    def container_type(self):
        """The container type/technology (e.g. - LXC, libContainer, etc.)"""
        return self.get('container_type')

    @property
    def default_container_name(self):
        """Name for default container (setup by fixture...)"""
        return self.get('default_container_name')

    @property
    def host_ip(self):
        """IP Address for system hosting the container."""
        return self.get('host_ip')

    @property
    def host_port(self):
        """Host port to connect to."""
        return int(self.get('host_port'))

    @property
    def container_ip(self):
        """Assigned IP for container (may be injected into config)"""
        return self.get('container_ip')

    @property
    def container_username(self):
        """Username to set/use to log into the container"""
        return self.get('container_username')

    @property
    def container_password(self):
        """Password to set/use to log into the container"""
        return self.get('container_password')

    @property
    def host_username(self):
        """Username to use to log into the container host"""
        return self.get('host_username')

    @property
    def host_password(self):
        """Password to use to log into the container host"""
        return self.get('host_password')

    @property
    def no_cleanup(self):
        """ Suppress cleanup of container after test."""
        return self.get_boolean('no_cleanup')

    @property
    def show_configs(self):
        """Show the container configs when operating on the container."""
        return self.get_boolean('show_configs')

    @property
    def primary_flavor(self):
        """Default container flavor to be used in compute tests."""
        return self.get("primary_flavor")

    @property
    def secondary_flavor(self):
        """Alternate container flavor to be used in compute tests."""
        return self.get("secondary_flavor")

    @property
    def primary_image(self):
        """Default container image to be used in compute tests."""
        return self.get("primary_image")

    @property
    def secondary_image(self):
        """Alternate container image to be used in compute tests."""
        return self.get("secondary_image")

    @property
    def lxc_cmd_delay(self):
        """LXC commands are slow to execute. Define delay between cmds"""
        return float(self.get("lxc_cmd_delay"))


class ContainerTestParameters(ConfigSectionInterface):
    """ Configuration of container-specific test parameters """
    SECTION_NAME = 'container_test_info'

    @property
    def virtualization_mem_limit_kb(self):
        """ Memory Allocation limit for Container """
        return int(self.get("virtualization_mem_limit_lxc_kb"))

    @property
    def virtualization_mem_tolerance_kb(self):
        """ Requested vs Allocated Memory Tolerance """
        return int(self.get("virtualization_mem_tolerance_kb"))

    @property
    def mkdir_depth(self):
        """ Depth of nested mkdirs for FileSystem Abuse tests """
        return int(self.get("mkdir_depth"))

    @property
    def temp_mkdir_dir(self):
        """ Name of temporary directory to nest for file system testing """
        DELIMITER = '/'
        directory = self.get("temp_mkdir_dir")
        if not directory.endswith(DELIMITER):
            directory = '{0}{1}'.format(directory, DELIMITER)
        return directory

    @property
    def max_fork_bomb_processes(self):
        """ Maximum number of processes to fork child processes """
        return int(self.get("max_fork_procs"))

    @property
    def host_pollution_username(self):
        """ Username to use for host pollution testing """
        return self.get('host_pollution_user')

    @property
    def debug(self):
        """ Get debug flag setting """
        return self.get_boolean('debug')
