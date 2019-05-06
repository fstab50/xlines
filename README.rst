
=======
 xlines
=======

--------------

Summary
-------

Count the number of lines of text in a code project (or anything else)

**Version**: 0.5.3

--------------

Contents
--------

-  `Getting Started <#getting-started>`__
-  `Dependencies <#dependencies>`__
-  `Help <#help>`__
-  `Exclusions <#exclusions>`__
-  `Screenshots <#screenshots>`__
-  `Author & Copyright <#author--copyright>`__
-  `License <#license>`__
-  `Disclaimer <#disclaimer>`__

--------------

Dependencies
------------

`xlines <https://github.com/fstab50/xlines>`__ requires python3.6+

`back to the top <#top>`__

--------------

Help
----

To display the help menu:

.. code:: bash

        $ xlines --help

|help|

`back to the top <#top>`__

--------------

Exclusions
----------

`xlines <https://github.com/fstab50/xlines>`__ maintains a list of file
types on the local filesystem that are excluded from line count totals.
To see this list of file types excluded from line count totals, type the
following:

.. code:: bash

        $ xlines --exclusions

|help|\

`back to the top <#top>`__

--------------

Screenshots
-----------

Counting lines in large repository with long paths.

.. code:: bash

        $ xlines  --sum  git/AWSAMPLES/aws-serverless-workshops/

|repo1-1|

`back to the top <#top>`__

--------------

Author & Copyright
------------------

All works contained herein copyrighted via below author unless work is
explicitly noted by an alternate author.

-  Copyright Blake Huber, All Rights Reserved.

`back to the top <#top>`__

--------------

License
-------

-  Software contained in this repo is licensed under the `license
   agreement <./LICENSE.md>`__. You may display the license and
   copyright information by issuing the following command:

::

    $ xlines --version

|help|

`back to the top <#top>`__

--------------

Disclaimer
----------

*Code is provided "as is". No liability is assumed by either the code's
originating author nor this repo's owner for their use at AWS or any
other facility. Furthermore, running function code at AWS may incur
monetary charges; in some cases, charges may be substantial. Charges are
the sole responsibility of the account holder executing code obtained
from this library.*

Additional terms may be found in the complete `license
agreement <./LICENSE.md>`__.

`back to the top <#top>`__

--------------

.. |help| image:: ./assets/help-menu.png
   :target: https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/help-menu.png
.. |help| image:: ./assets/exclusions.png
   :target: https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/exclusions.png
.. |repo1-1| image:: ./assets/repofinal.png
   :target: https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/repofinal.png
.. |help| image:: ./assets/version-copyright.png
   :target: https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/version-copyright.png
