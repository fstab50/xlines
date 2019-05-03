"""
Summary.

    Commons Module -- Common Functionality

"""


class ExcludedTypes():
    def __init__(self, ex_path, ex_container=[]):
        self.types = ex_container
        if not self.types:
            self.types.extend(self.parse_exclusions(ex_path))

    def excluded(self, path):
        for i in self.types:
            if i in path:
                return True
        return False

    def parse_exclusions(self, path):
        """
        Parse persistent fs location store for file extensions to exclude
        """
        try:
            return [x.strip() for x in open(path).readlines()]
        except OSError:
            return []


def remove_duplicates(duplicates):
    """
    Summary.

        Module function utilsing a generator to remove duplicates
        from large scale lists with minimal resource use

    Args:
        duplicates (list): contains repeated elements

    Returns:
        generator object (iter)
    """
    uniq = []

    def dedup(d):
        for element in d:
            if element not in uniq:
                uniq.append(element)
                yield element
    return [x for x in dedup(duplicates)]


def remove_illegal(d, illegal):
    """Removes excluded file types"""
    bad = []

    for path in d:
        for t in illegal:
            if t in path:
                bad.append(path)
    return list(filter(lambda x: x not in bad, d))


def locate_fileobjects(origin, path=expath):
    """
    Summary.

        - Walks local fs directories identifying all git repositories

    Args:
        - origin (str): filesystem directory location

    Returns:
        - paths, TYPE: list
        - Format:

         .. code-block:: json

                [
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/utils_email.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/slack_delivery.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/datadog_delivery.py',
                    '/cloud-custodian/tools/c7n_sentry/setup.py',
                    '/cloud-custodian/tools/c7n_sentry/test_sentry.py',
                    '/cloud-custodian/tools/c7n_kube/setup.py',
                    '...
                ]

    """
    fobjects = []
    ex = ExcludedTypes(path)

    if os.path.isfile(origin):
        return [origin]

    for root, dirs, files in os.walk(origin):
        for file in [f for f in files if '.git' not in root]:
            try:

                full_path = os.path.abspath(os.path.join(root, file))

                #if not ex.excluded(full_path):
                fobjects.append(full_path)

            except OSError:
                logger.exception(
                    '%s: Read error while examining local filesystem path (%s)' %
                    (inspect.stack()[0][3], path)
                )
                continue
    return remove_duplicates(fobjects)
