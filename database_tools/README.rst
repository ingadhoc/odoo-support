.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Database Tools
==============

This module add mainly two functionalities:

* Database backups

This module depends on "server_mode" module so backups can be disable by server_mode

Please check this `presentation
<https://docs.google.com/presentation/d/1_moDG_l9DJYio48vebAR15mhARFt-UT3h6qQYON0vEk/pub?start=false&loop=false&delayms=3000>`_

Installation
============

To install this module, you need to:

#. Install fabric with "pip install fabric"

Configuration and usage
=======================

To configure this module, you need to:

#. Backups:
    * by default backups are disable, you can enable them with "database.backups.enable" parameter
    * by default a database record is created for the database where you've installed this module. You can check this record on "Settings / Database Tools / Databases"
    * Some default preservation rules are loaded, you can modify them at your own need
    * You can restore database remotly by calling "restore_db" WS
    * You can check database backup status on "Settings / Configuration / Database Tools"
#. Modules update management:
    * Database modules status and fixes can be run on "Settings / Configuration / Database Tools"
    * If database isn't accessible you can try to fix it by running something like "http://localhost:8069/fix_db/<db_name>"

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.adhoc.com.ar/

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* ADHOC SA: `Icon <http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png>`_.

Contributors
------------


Maintainer
----------

.. image:: http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png
   :alt: Odoo Community Association
   :target: https://www.adhoc.com.ar

This module is maintained by the ADHOC SA.

To contribute to this module, please visit https://www.adhoc.com.ar.