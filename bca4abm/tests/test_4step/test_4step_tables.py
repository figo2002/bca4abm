import os.path

import numpy.testing as npt
import pandas as pd
import orca
import pandas.util.testing as pdt
import pytest


# orca injectables complicate matters because the decorators are executed at module load time
# and since py.test collects modules and loads them at the start of a run
# if a test method does something that has a lasting side-effect, then that side effect
# will carry over not just to subsequent test functions, but to subsequently called modules
# for instance, columns added with add_column will remain attached to orca tables
# pytest-xdist allows us to run py.test with the --boxed option which runs every function
# with a brand new python interpreter
# py.test --boxed --cov bca4abm

# Also note that the following import statement has the side-effect of registering injectables:
from bca4abm import bca4abm as bca

from bca4abm.util.misc import expect_columns, missing_columns, extra_columns, mapped_columns


@pytest.fixture(scope="module", autouse=True)
def inject_default_directories(request):

    parent_dir = os.path.dirname(__file__)
    orca.add_injectable("configs_dir", os.path.join(parent_dir, 'configs'))
    orca.add_injectable("data_dir", os.path.join(parent_dir, 'data'))
    orca.add_injectable("output_dir", os.path.join(parent_dir, 'output'))

    request.addfinalizer(orca.clear_cache)


def test_settings():

    settings = orca.eval_variable('settings')
    assert settings.get('provenance') == 'tests.4step.configs'


# def test_read_zone_demographics_table():
#
#     settings = orca.eval_variable('settings')
#
#     assert settings.get('zone_demographics') == 'zone_demographics.csv'
#     assert orca.eval_variable('input_source') == 'read_from_csv'
#
#     # expect all of and only the columns specified by persons_column_map values
#     zones = orca.get_table('zone_demographics').to_frame()
#     # assert expect_columns(persons,
#     #                       settings['persons_column_map'].values())
#
#     assert zones.shape[0] == 25


