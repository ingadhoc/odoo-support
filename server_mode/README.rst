.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========
Server Mode
===========

This modules disable some functions when running databases on odoo servers with
parameter server_mode = "some value". It will show a ribbon in the instance
which text will be the value saved in server_mode paramater: if this one is
not set then will not show any ribbon.

This module already disable this things on none production environments:

#. Disable send mail
#. Disable Fetchmail
#. Disable odoo crons

   **NOTE** Maybe we see that is better to use activated ir.cron in a not production environment, in this case we can disable them in the odoo.conf using entrypoint.sh taking into account the environment type or any other parameter that could disable them.


This module is also inherited by other modules so that you can disable
functionalities depending on server mode. To use it:

* import with: from openerp.addons.server_mode.mode import get_mode
* use it like any of the following::

   if get_mode() == 'test':
   if get_mode() == 'develop'
   if get_mode():

Installation
============

To install this module, you do not need to anything, just install this module.

Configuration
=============

To configure this module, you need to:

* Set a parameter on your odoo.conf file lie "server_mode = test"

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/odoo-support/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
