<a name="top"></a>
* * *
# xlines
* * *

## Summary

Count the number of lines of text in a code project (or anything else)

**Version**: 0.6.8

* * *

## Contents

* [Getting Started](#getting-started)
* [Dependencies](#dependencies)
* [Help](#help)
* [Exclusions](#exclusions)
* [Screenshots](#screenshots)
* [Author & Copyright](#author--copyright)
* [License](#license)
* [Disclaimer](#disclaimer)

* * *

## Dependencies

[xlines](https://github.com/fstab50/xlines) requires python3.6+


[back to the top](#top)

* * *
## Help

To display the help menu:

```bash
    $ xlines --help
```

[![help](./assets/help-menu.png)](https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/help-menu.png)


[back to the top](#top)

* * *
## Exclusions

[xlines](https://github.com/fstab50/xlines) maintains a list of file types on the local filesystem that are excluded from line count totals.  To see this list of file types excluded from line count totals, type the following:

```bash
    $ xlines --exclusions
```

[![help](./assets/exclusions.png)](https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/exclusions.png)<!-- .element height="50%" width="50%" -->


[back to the top](#top)

* * *
## Screenshots

Counting lines in large repository with long paths.

```bash
    $ xlines  --sum  git/AWSAMPLES/aws-serverless-workshops/
```

[![repo1-1](./assets/repofinal.png)](https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/repofinal.png)


[back to the top](#top)

* * *

## Author & Copyright

All works contained herein copyrighted via below author unless work is explicitly noted by an alternate author.

* Copyright Blake Huber, All Rights Reserved.

[back to the top](#top)

* * *

## License

* Software contained in this repo is licensed under the [license agreement](./LICENSE.md).  You may display the license and copyright information by issuing the following command:

```
$ xlines --version
```

[![help](./assets/version-copyright.png)](https://s3.us-east-2.amazonaws.com/http-imagestore/xlines/version-copyright.png)


[back to the top](#top)

* * *

## Disclaimer

*Code is provided "as is". No liability is assumed by either the code's originating author nor this repo's owner for their use at AWS or any other facility. Furthermore, running function code at AWS may incur monetary charges; in some cases, charges may be substantial. Charges are the sole responsibility of the account holder executing code obtained from this library.*

Additional terms may be found in the complete [license agreement](./LICENSE.md).

[back to the top](#top)

* * *
