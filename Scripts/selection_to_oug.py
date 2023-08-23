"""
Script to merge a selection of parcels into one parcel 
    within an existing feature class

Author: Lilah Rosenfield (lrosenfield@wfrc.org)
Organization: Wasatch Front Regional Council
Version: August 23, 2023
"""

import arcpy
import arcpy.management as arcmg
from pprint import pformat as pf
import arcscripttools as st
import unionmerge as um


def script_tool(parcel_layer, modified_fields, prop_type):
    """
    Script code goes below
    """
    units = r"memory\interior_units_mem"
    remapped = r"memory\rmp_mem"

    st.validate_selection(parcel_layer, 50)

    st.loginfo(f"Running Selection to OUG with {um.PROCESSOR_VERSION}")

    un_c = arcmg.GetCount(parcel_layer)
    st.loginfo(f'Layers by location has {un_c} units')

    arcmg.CopyFeatures(parcel_layer, units)

    solvent = um.create_dissolve_stats(units, modified_fields)

    um.dissolve_and_rectify(units, solvent, remapped)

    arcmg.CalculateField(
        in_table=remapped,
        field="SUBPROCESSOR",
        expression="'" + "Selected Parcel Merge" + "'",
        expression_type="PYTHON3",
    )

    arcmg.CalculateField(
        in_table=remapped,
        field="SUBTYPE",
        expression="'" + prop_type + "'",
        expression_type="PYTHON3",
    )

    arcmg.Append(
        inputs = remapped,
        target = parcel_layer,
        schema_type = "TEST"
    )

    arcmg.DeleteRows(parcel_layer)

    return


if __name__ == "__main__":

    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameter(1)
    param2 = arcpy.GetParameterAsText(2)

    script_tool(param0, param1, param2)
    #arcpy.SetParameterAsText(2, "Result")