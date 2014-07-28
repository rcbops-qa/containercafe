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

Purpose: Given a container technology (LXC, libContainer) and a connection type
        (ssh, API, local), build a "universal" client for consumption by the
        tests and behaviors.

"""

# Containers
from ..clients.host import HostContainerClient
from ...lxc.client import LxcContainer

# Connections
from cafe.engine.ssh.client import BaseSSHClient


class UnknownContainerType(Exception):
    def __init__(self, type_, **kwargs):
        super(UnknownContainerType, self).__init__(**kwargs)
        self.message = "Unrecognized container type: {type_}".format(
            type_=type_)


class UnknownTargetType(Exception):
    def __init__(self, type_, types_list, **kwargs):
        super(UnknownTargetType, self).__init__(**kwargs)
        self.message = ("Unrecognized target type: {type_} "
                        "[{types}]".format(type_=type_,
                                           types=", ".join(types_list)))


class UnknownClientAPI(Exception):
    def __init__(self, api_name):
        super(UnknownClientAPI, self).__init__()
        self.message = 'Unrecognized client API: {api}'.format(api=api_name)


class UnableToConnect(Exception):
    def __init__(self, ip, port, user, pswd):
        super(UnableToConnect, self).__init__()
        self.message = ('Unable to reach/connect to {ip}:{port} as '
                        '{user}/{pswd}'.format(ip=ip, port=port, user=user,
                                               pswd=pswd))


class BuildContainerClient(object):

    # Set to TRUE if the container cannot be reached externally
    ISOLATED_CONTAINER = True

    # Types of supported container technologies
    LXC = 'lxc'

    # Type of test targets
    HOST = 'host'                            # ssh to host
    LOCAL = 'local_host'                     # ssh to host
    HOST_TO_CONTAINER = 'host_to_container'  # ssh to host
    CONTAINER = 'container'                  # ssh to container

    # ContainerType and ConnectionType class registrations
    CONTAINER_TYPES = [LXC]
    CONTAINER_CLASS = {HOST: {LXC: HostContainerClient},
                       HOST_TO_CONTAINER: {LXC: LxcContainer},
                       LOCAL: {LXC: HostContainerClient},
                       CONTAINER: {LXC: HostContainerClient}}

    # Miscellaneous Constants
    TARGET_TYPES = [HOST, HOST_TO_CONTAINER, LOCAL, CONTAINER]
    RC_FILE = 'rc_file'

    def __init__(self, container_type, test_ref_point,
                 test_config, container_config, container_name,
                 rc_file=None, username=None, password=None,
                 port=None, clean=True):
        self.container_name = container_name
        self.container_type = container_type
        self.container_config = container_config
        self.test_ref_point = test_ref_point    # HOST OR CONTAINER
        self.test_config = test_config
        self.rc_file = rc_file
        self.username = username
        self.password = password
        self.port = port or self.container_config.host_port
        self.clean = clean

        self.type_ = 'host'
        if not self.ISOLATED_CONTAINER:
            if self.test_ref_point == self.CONTAINER:
                self.type_ = self.CONTAINER

        if self.username is None:
            self.username = getattr(
                self.container_config, '{0}_username'.format(self.type_))

        if self.password is None:
            self.password = getattr(
                self.container_config, '{0}_password'.format(self.type_))

    def get_client(self, container_type=None, test_ref_point=None,
                   clean=None, container_name=None, username=None,
                   password=None, port=None):

        # Use values provided or use factory defaults
        container_type = container_type or self.container_type
        test_ref_point = test_ref_point or self.test_ref_point
        container_name = container_name or self.container_name
        port = port or self.port
        username = username or self.username
        password = password or self.password
        clean = clean or self.clean
        kwargs = dict()

        # Verify client config info is valid...
        if container_type not in self.CONTAINER_TYPES:
            raise UnknownContainerType(type_=container_type)

        if test_ref_point not in self.TARGET_TYPES:
            raise UnknownTargetType(type_=test_ref_point,
                                    types_list=self.TARGET_TYPES)

        # Get the corresponding container and connection type
        cntnr_cls = self.CONTAINER_CLASS[self.test_ref_point][container_type]
        target_type_ip = getattr(self.container_config, '{0}_ip'.format(
            self.type_))

        # Verify connection_info is correct...
        if True:
            print ""
            print "CONTAINER_TYPE:", container_type
            print "REFERENCE TYPE:", test_ref_point
            print "CONTAINER CLASS: ", cntnr_cls
            print "TYPE_:", self.type_
            print "CONN TARGET: {user}@{ip}:{port} --> '{pswd}'".format(
                ip=target_type_ip, port=port, user=username, pswd=password)
            print ""

        # Create a common alias between clients: client.execute = reference to
        # function used for executing command based on the type of connection.
        connection = BaseSSHClient(target_type_ip)
        connection.connect(username=username, password=password, port=port)
        if connection.ssh_connection is None:
            raise UnableToConnect(ip=target_type_ip, port=port, user=username,
                                  pswd=password)
        connection.start_shell()
        connection.execute = connection.execute_shell_command
        connection.close = connection.end_shell

        # For now, if connecting to the container, connect to the VM (host),
        # then ssh from the host to the container. Eventually, this will not
        # be needed, when the container is publicly reachable (not isolated
        # within a private VM)
        if (self.test_ref_point == self.CONTAINER and
                self.ISOLATED_CONTAINER):
            connected = self._connect_to_container_through_host(
                connection=connection)
            if not connected:
                return None

        # Instantiate the container client
        container_client = cntnr_cls(name=container_name,
                                     connection=connection,
                                     clean=clean, **kwargs)

        # LXC directives are slow to execute. They return, but the cmd may not
        # have fully executed on the host yet, so a delay can be introduced
        # between command executions.
        if isinstance(container_client, LxcContainer):
            container_client.cmd_delay = self.container_config.lxc_cmd_delay

        # Store the client's test_reference_point: some tests require to be
        # executed from a specific container-context
        container_client.test_reference_point = test_ref_point

        return container_client

    def _connect_to_container_through_host(self, connection):
        wait_for = 10  # Seconds
        success = None

        container_ip = self.container_config.container_ip
        container_user = self.container_config.container_username
        container_pswd = self.container_config.container_password

        ssh_cmd = 'ssh {user}@{ip}'.format(user=container_user,
                                           ip=container_ip)
        login = connection.execute_shell_command(cmd=ssh_cmd, prompt=':',
                                                 timeout=wait_for)
        if login.stderr is not None:
            print "SSH TO CONTAINER ERR:", login.stderr
            success = False

        auth = connection.execute_shell_command(cmd=container_pswd,
                                                timeout=wait_for)
        if auth.stderr is not None:
            print "AUTHENTICATE TO CONTAINER ERR:", login.stderr
            success = False

        if success is None:
            success = True

        return success
