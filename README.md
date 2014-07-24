ContainerCAFE
================================
<pre>
   _ _ _
  ( `   )_
 (    )   `)  _
(____(__.___`)__)

    ( (
       ) )
    .........
    |       |___
    |       |_  |
    |  :-)  |_| |
    |       |___|
    |_______|
=== ContainersCAFE ===

</pre>

ContainerCAFE is an extension of the [CloudCAFE Framework](https://github.com/stackforge) specifically designed to test deployed
versions of Rackspace's Containers product. It is built using the [Open CAFE Core](https://github.com/stackforge) and [CloudCAFE](https://github.com/stackforge)

Supported Operating Systems
---------------------------
ContainerCAFE has been developed primarily in Linux and MAC environments, however, it supports installation and
execution on Windows

Installation
------------
ContainerCAFE can be [installed with pip](https://pypi.python.org/pypi/pip) from the git repository after it is cloned to a local machine.

* First follow the README instructions to install [CloudCAFE](https://github.com/stackforge)
* Clone this repository to your local machine
* CD to the root directory in your cloned repository.
* Run "[sudo] pip install . --upgrade" and pip will auto install all other dependencies.

Configuration
--------------
ContainerCAFE works in tandem with the [Open CAFE Core](https://github.com/stackforge) cafe-runner. This installation of CloudCAFE includes a reference
configuration for each of the CloudCAFE supported OpenStack products. Configurations will be installed to: <USER_HOME>/.opencafe/configs/<PRODUCT>

To use ContainerCAFE you **will need to create/install your own configurations** based on the reference configs pointing to your deployment of OpenStack.

At this stage you will have the Open CAFE Core engine and the CloudCAFE Framework implementation. From this point you are ready to:
1) Write entirely new tests using the CloudCAFE Framework
					or
2) Install the [CloudRoast Test Repository](https://github.com/stackforge), an Open Source body of OpenStack automated tests written with CloudCAFE
that can be executed or extended. You can also install the ContainersRoast Test Repository, which are the automated tests writeen for ContainersCAFE that can be executed or extended.

Logging
-------
ContainerCAFE leverages the logging capabilities of the CAFE Core engine. If tests are executed with the built-in cafe-runner, runtime logs will be output
to <USER_HOME>/.opencafe/logs/<PRODUCT>/<CONFIGURATION>/<TIME_STAMP>. In addition, tests built from the built-in CAFE unittest driver will generate
csv statistics files in <USER_HOME>/.opencafe/logs/<PRODUCT>/<CONFIGURATION>/statistics for each and ever execution of each and every test case that
provides metrics of execution over time for elapsed time, pass/fail rates, etc...

Basic ContainerCAFE Package Anatomy
-------------------------------
Below is a short description of the top level ContainersCAFE Packages.

##containercafe
This is the root package for all things ContainerCAFE.

##common
Contains modules that extend the CAFE Core engine specific to OpenStack. This is the primary namespace for tools, data generators, common
reporting classes, etc...

##configs
Configuration files that are needed to run automated tests.

##metatests
Unit tests for ContainersCAFE

