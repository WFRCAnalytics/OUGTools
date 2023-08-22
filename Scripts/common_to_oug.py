"""
Script to merge parcels within a common area 
    into Owned Unit Groupings (OUGs)

Author: Lilah Rosenfield (lrosenfield@wfrc.org)
Organization: Wasatch Front Regional Council
Version: June 7, 2023
"""
import arcpy
import arcpy.management as arcmg
from pprint import pformat as pf
import arcscripttools as st
import unionmerge as um


def script_tool(common_parcel_layer, review_parcel_layer, modified_fields):
    """
    Script code goes below
    """
    cmn_prcl = r"memory\common_parcel_mem"
    units = r"memory\interior_units_mem"
    remapped = r"memory\rmp_mem"

    st.validate_selection(common_parcel_layer, 2)
    
    st.loginfo(f"Running Common Parcel to OUG with {um.PROCESSOR_VERSION}")

    # Unfortunately requires ArcPro License
    arcmg.EliminatePolygonPart(
        in_features=common_parcel_layer,
        out_feature_class=cmn_prcl,
        condition="PERCENT",
        part_area="0 SquareMeters",
        part_area_percent=90,
        part_option="CONTAINED_ONLY"
    )
    st.clear_selection(common_parcel_layer)

    layersByLoc = arcmg.SelectLayerByLocation(
        in_layer=review_parcel_layer,
        overlap_type="WITHIN",
        select_features=cmn_prcl,
        search_distance=None,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="NOT_INVERT"
    )

    lbl_c = arcmg.GetCount(layersByLoc)
    st.loginfo(f'Layers by location has {lbl_c} units')

    #st.loginfo(type(interior_units))

    arcmg.CopyFeatures(layersByLoc,units)
    ium_c = arcmg.GetCount(units)
    st.loginfo(f'there are {ium_c} units in the new dataset')

    # Always check if you need to spend time programming something folks
    #conform_attribute_table(units, cmn_prcl)
    # The functions I wrote for this can be found in a separate script

    solvent = um.create_dissolve_stats(units,modified_fields)

    arcmg.Append(
        inputs = cmn_prcl, target = units, schema_type = "NO_TEST"
        )

    # arcmg.CopyFeatures(r'memory\interior_units_mem',param2)
    
   
    # arcmg.CopyFeatures(solution, "workingTest")
    um.dissolve_and_rectify(units, solvent, remapped)
    
    #st.loginfo(pf(map.exportToString()))
    # arcmg.CopyFeatures(units, "workingTest")

    arcmg.CalculateField(
        in_table=remapped,
        field="SUBPROCESSOR",
        expression="'" + "Common Parcel Merge" + "'",
        expression_type="PYTHON3",
    )

    # raise arcpy.ExecuteError()
    arcmg.Append(
        inputs = remapped,
        target= review_parcel_layer,
        schema_type="TEST"
    )

    arcmg.DeleteRows(layersByLoc)
    #st.clear_selection(review_parcel_layer)

    return


if __name__ == "__main__":
    #arcpy.AddError("Script failed (as a test)")
    st.loginfo("Script is still running")
    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)
    # Quick 'n dirty param removal
    param3 = arcpy.GetParameter(2)

    script_tool(param0, param1, param3)
    #st.clear_selection(param0)
    #st.clear_selection(param1)
    #arcpy.SetParameterAsText(2, "Result")

