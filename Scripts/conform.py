"""
Script documentation

NOTE THIS SCRIPT HAS NOT BEEN THOROUGHLY TESTED.
PLEASE USE WITH CAUTION

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()

Author: Lilah Rosenfield (lrosenfield@wfrc.org)
Organization: Wasatch Front Regional Council
Version: May 25, 2023
"""
import arcpy
import arcpy.management as arcmg
import time

from pprint import pformat as pf

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


def list_field_names(layer):
    """
    Returns a list containing all field names for a given layer

    Parameter: layer
    Condition: a string describing a valid layer in the ArcPy environment
    """
    layer_names = []
    layer_fields = arcpy.ListFields(layer)

    for field in layer_fields:
        layer_names.append(field.name)
    return layer_names


def add_fields(old_fl, new_fl, fields):
    """
    Adds correctly typed fields to new_fl

    We want to add fields named 'fields' found in old_fl to new_fl
    with their correct type.

    Parameter old_fl: the layer to pull field types from
    Condition: a string describing a valid layer in the ArcPy environment
    
    Parameter new_fl: the layer to add new fields to
    Condition: a string describing a valid layer in the ArcPy environment
    
    Parameter fields: a list of fields to add to new_fl  
    Conditions:  
        - fields must be a list
        - fields must only contain field names
        - fields must only contain fields names found in old_fl
        - fields must not contain field names already found in new_fl
    """
    for f in fields:
        typ = arcpy.ListFields(old_fl,wild_card=f)[0].type
        loginfo(f"adding field named {f} of type {typ} to the attribute table")
        arcmg.AddField(new_fl,f, typ)


def script_tool(conform_to, trg):
    """
    Modifies the attribute table of trg to that of conform_to

    Useful if you want to automate the process of appending trg to
    conform_to without having to know what layers specifically are present
    
    This function modifies layer trg, keeping conform_to untouched

    Parameter conform_to: the layer which has the desired attribute table
    Condition: a string describing a valid layer in the ArcPy environment

    Parameter trg: the target layer whose attribute table will be modified
    Condition: a string describing a valid layer in the ArcPy environment
    """
    loginfo("Conforming attribute tables")
    unmofidied_fields = {"Shape_Length", "Shape_Area", 
                         "SHAPE_Length", "SHAPE_Area",
                         "SHAPE", "Shape"}
    
    new_table = list_field_names(conform_to)
    existing_table = list_field_names(trg)

    loginfo(f"Target table contains {len(existing_table)} fields")
    loginfo(f"Template table contains {len(new_table)} fields")
    ntb_set = set(new_table)
    extb_set = set(existing_table)
    tbrm = extb_set - ntb_set - unmofidied_fields
    tbad = ntb_set - extb_set - unmofidied_fields
    exov = ntb_set & extb_set
    loginfo(f"The following attributes are present in both sets:")
    loginfo(pf(exov))
    loginfo(f"the following attributes will be removed:")
    loginfo(pf(tbrm))
    loginfo(f"the following attributes will be added:")
    loginfo(pf(tbad))

    arcmg.DeleteField(trg, list(tbrm))
    add_fields(conform_to, trg, list(tbad))

    loginfo("Target field now has the following attribute fields")
    loginfo(pf(list_field_names(trg)))
    loginfo("Compare to source")
    loginfo(pf(list_field_names(conform_to)))
    return


if __name__ == "__main__":

    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)

    script_tool(param0, param1)
    arcpy.SetParameterAsText(2, "Result")