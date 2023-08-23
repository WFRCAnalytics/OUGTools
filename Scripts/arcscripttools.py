"""
Collection of basic script tools to be used as part of the OUG Merge Toolbox

Author: Lilah Rosenfield (lrosenfield@wfrc.org)
Organization: Wasatch Front Regional Council
Version: August 23, 2023
"""

import arcpy
import arcpy.management as arcmg
import time
from pprint import pformat as pf
INSOLUBLES = ["OBJECTID", "Shape", "Shape_Length", "Shape_Area"]

def clear_selection(pram):
    """
    Quick layer selection clear function

    Parameter pram: The layer to clear.
    Condition: a string describing a valid layer in the ArcPy environment
    """
    arcmg.SelectLayerByAttribute(pram, "CLEAR_SELECTION")
    return


def loginfo(msw, loglevel=1):
    """
    Functional wrapper to log messages. Use as you would print()
    
    Converts a message to a string, then add it 
    to the geoprocessing output.

    If loglevel == 1, msw will also be appended to logfile
    along with the time

    Parameter msw: The message you want sent.
    Condition: none

    Parameter loglevel: the logging level [1 or 0]
    """
    msg = str(msw)
    if loglevel == 1:

        log = open("logfile",'a')
        log.write('\n' + time.asctime() + ' - ')
        log.write(msg)
        log.close()
        arcpy.AddMessage(msg)

    else:
        arcpy.AddMessage(msg)

    return


def validate_selection(layer_to_check, count):
    """
    Ensures the num. of parcels selected in *common_parc* is less than *count*

    Adds an error and raises an ExecuteError if not

    Parameter layer_to_check: The layer to check
    Condition: a string describing a valid layer in the ArcPy environment
    """
    count_y = int(arcmg.GetCount(layer_to_check)[0])
    if count_y >= count:
        arcpy.AddError("Common parcel must have one selection! " \
                      f"(Currently has {count_y})")
        raise arcpy.ExecuteError()


def bulk_validate(layer, text):
    """
    Marks a selected group of parcels as complete with a processing method

    Parameter layer: the layer to modify
    Condition: a string describing a valid layer in the ArcPy environment

    Parameter text: the text identifying the processor
    Condition: a string no longer than 255 Characters
    """
    arcmg.CalculateField(
        in_table=layer,
        field="COMPLETE",
        expression=1,
        expression_type="PYTHON3",
    )

    arcmg.CalculateField(
        in_table=layer,
        field="PROCESSOR",
        expression="'" + text + "'",
        expression_type="PYTHON3",
    )