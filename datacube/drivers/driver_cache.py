from __future__ import absolute_import, print_function

import logging

from pkg_resources import iter_entry_points, DistributionNotFound

_LOG = logging.getLogger(__name__)


def load_drivers(group):
    """
    Load available drivers for a given group name.

    Gracefully handles:

     - Driver module not able to be imported
     - Driver init function throwing an exception or returning None

     By having driver entry_points pointing to a function, we defer loading the driver
     module or running any code until required.

    :param str group: Name of the entry point group e.g. "datacube.plugins.io.read"

    :returns: Dictionary String -> Driver Object
    """

    def safe_load(ep):
        # pylint: disable=bare-except
        try:
            driver_init = ep.load()
        except DistributionNotFound:
            # This happens when entry points were marked with extra features,
            # but extra feature were not requested for installation
            return None
        except:
            _LOG.warning('Failed to resolve driver %s::%s', group, ep.name)
            return None

        try:
            driver = driver_init()
        except:
            _LOG.warning('Exception during driver init, driver name: %s::%s', group, ep.name)
            return None

        if driver is None:
            _LOG.warning('Driver init returned None, driver name: %s::%s', group, ep.name)

        return driver

    def resolve_all(group):
        for ep in iter_entry_points(group=group, name=None):
            driver = safe_load(ep)
            if driver is not None:
                yield (ep.name, driver)

    return dict((name, driver) for name, driver in resolve_all(group))
