# bca4abm
# See full license in LICENSE.txt.

import logging

import os
import pandas as pd
import numpy as np


from bca4abm import bca4abm as bca

from ...util.misc import add_aggregate_results

from activitysim.core import config
from activitysim.core import inject
from activitysim.core import tracing
from activitysim.core import assign
from activitysim.core import pipeline

logger = logging.getLogger(__name__)

"""
Aggregate zone processor

each row in the data table to solve is an origin zone and this
processor calculates zonal auto ownership differences as well as the
differences in the destination choice logsums - ma.<purpose|income>dcls.csv
Maybe the ma.<purpose|income>dcls.csv files should be added to the
mf.cval.csv before input to the bca tool?
"""


@inject.injectable()
def aggregate_zone_spec(configs_dir):

    f = os.path.join(configs_dir, "aggregate_zone.csv")
    return bca.read_assignment_spec(f)


@inject.injectable()
def aggregate_zone_settings(configs_dir):
    return config.read_model_settings(configs_dir, 'aggregate_zone.yaml')


@inject.step()
def aggregate_zone_processor(
        zones,
        aggregate_zone_spec,
        aggregate_zone_settings,
        settings, trace_od):
    """
    zones: orca table

    zone data for base and build scenario dat files combined into a single dataframe
    with columns names prefixed with 'base_' or 'build_' indexed by ZONE
    """

    zones_df = zones.to_frame()

    logger.info("Running aggregate_zone_processor with %d zones"
                % (len(zones_df.index), ))

    if trace_od:
        trace_orig, trace_dest = trace_od
        trace_od_rows = (zones_df.index == trace_orig) | (zones_df.index == trace_dest)
    else:
        trace_od_rows = None

    # locals whose values will be accessible to the execution context
    # when the expressions in spec are applied to choosers
    locals_dict = config.get_model_constants(aggregate_zone_settings)
    locals_dict.update(config.setting('globals'))

    trace_rows = None

    # eval_variables evaluates each of the expressions in spec
    # in the context of each row in of the choosers dataframe
    results, trace_results, trace_assigned_locals = \
        assign.assign_variables(aggregate_zone_spec,
                                zones_df,
                                locals_dict,
                                df_alias='zones',
                                trace_rows=trace_od_rows)

    pipeline.replace_table('aggregate_zone_benefits', results)

    add_aggregate_results(results, aggregate_zone_spec, source='aggregate_zone')


    if trace_results is not None:

        # tracing.write_csv(results,
        #                   file_name="aggregate_zone_results",
        #                   transpose=False)

        tracing.write_csv(trace_results,
                          file_name="aggregate_zone",
                          index_label='zone',
                          column_labels=['label', 'zone'])

        if trace_assigned_locals:
            tracing.write_csv(trace_assigned_locals, file_name="aggregate_zone_locals")


