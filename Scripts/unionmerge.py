"""
Module containing various tools to help ArcPy
    merge a group of parcels into one parcel
    within an existing feature class

The group of parcels is usually passed by an ArcGIS Script tool

Author: Lilah Rosenfield (lrosenfield@wfrc.org)
Organization: Wasatch Front Regional Council
Version: June 7, 2023
"""

import arcpy
import arcpy.management as arcmg
from pprint import pformat as pf
import arcscripttools as st

solution = r"memory\dissolved"
PROCESSOR_VERSION = "OUG Merge Processor v1.0"
#solu_remap = r"memory\srmp"

def handle_bad_str_op(lyr, fld, op):
    """
    Eventually should be able to remap a text field containing just integers
    into an integer field so dissolve actually works.

    For now, just throws an error.
    """
    arcpy.AddError(f"Cannot perform operation operation {op} " \
                   f"on field {fld} with type 'string' ")
    raise arcpy.ExecuteError()

def vt_to_dict(vt):
    """
    Returns an array (list of lists) from a given arcPy Value Table

    Parameter vt: the value table to convert
    Condition: vt must be an arcpy ValueTable object 
               with two columns
    """
    st.loginfo("Converting ValueTable to dictionary")
    field_rows = vt.rowCount
    field_dict = {}
    for i in range(field_rows):
        row = vt.getTrueRow(i)
        #st.loginfo(f"ValueTable row is {row}, and object is {row[0].value}")
        field_dict[row[0].value] = row[1]
    st.loginfo("Field dictionary constructed:")
    st.loginfo(pf(field_dict))
    return field_dict


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


def create_dissolve_stats(lyr, field_ops):
    """
    Returns a ValueTable for use as a dissolve statistics_field

    All values of the layer will be set for inclusion in the
    dissolved dataset. Any fields for which different features
    have different values MUST HAVE A VALID OPERATION provided
    by the field_ops parameter. If they do not, this function
    throws a KeyError.

    If all features have the same value for a given field
    and no operation is provided by the field_ops parameter
    then the statistics operation will be set to "FIRST"
    (so the same value for all objects is carried over)

    Parameter layer: the  layer to be dissolved
    Condition: a string describing a valid layer in the ArcPy environment

    Parameter field_ops: the ValueTable describing operations
    Conditions: 
        - field_ops is a value table
        - field_ops column 1 contains only fields found in layer
        - all fields for which different features in layer 
            have different attributes in a given field
            must be present in field_ops and have
            an associated valid operation
    """
    #st.loginfo(f"Creating the dissolution table from {field_ops}")
    
    # GET IT?? 😜

    user_op_dict = vt_to_dict(field_ops)
    lfn = list_field_names(lyr)
    solvent = arcpy.ValueTable(2)

    # Buld out the ValueTable to pass to the Dissolve tool
    for attr_col in lfn:

        # User operation preferences always take precedence
        if attr_col in list(user_op_dict):
            
            if attr_col in st.INSOLUBLES:
                arcpy.AddError("Cannot combine system-managed values! "\
                               "please make sure " + str(st.INSOLUBLES) + \
                               " are not in the provided field map!")
                raise arcpy.ExecuteError()
            # Because we're going to append the common parcel
            # It should always be last
            if user_op_dict[attr_col] == "Common Attribute":
                solvent.addRow([attr_col, "LAST"])
            
            # Otherwise, the user specifies the same operation we want to use
            else:
                ft = arcpy.ListFields(lyr, attr_col)[0].type
                logstr = f"for {attr_col}, field type is {ft}"
                st.loginfo(logstr)
                if ft == 'String':
                    if user_op_dict[attr_col] != 'FIRST':
                        handle_bad_str_op(lyr, attr_col, user_op_dict[attr_col])
                solvent.addRow([attr_col, user_op_dict[attr_col]])
        
        # But if a user didn't specifiy an operation...
        else:
            attr_list = list(arcpy.da.SearchCursor(lyr, field_names=attr_col))
            
            # Double check that the attributes are the same 
            if not (all(ele == attr_list[0] for ele in attr_list) 
                    or attr_col in st.INSOLUBLES):
                arcpy.AddError(f"Attributes in column {attr_col} "\
                               "vary between features, but no "\
                               "operation was provided to combine them!")
                raise arcpy.ExecuteError()
            elif not attr_col in st.INSOLUBLES:
                solvent.addRow([attr_col, "FIRST"]) 
                # Or second or third or fourth. 
                # Point is, they should all be the same.
    
    st.loginfo("Created Dissolve list with the following rules")
    st.loginfo(solvent.exportToString())
    return solvent


def field_map_for_dict(inputDataset, mappingDict):
    """
    Uses a simple mapping dictionary to build a FieldMap

    With much thanks to 
    [Son of A Beach](https://gis.stackexchange.com/users/18859/son-of-a-beach) 
    on [GIS StackExchange](https://gis.stackexchange.com/questions/328425/using-field-mapping-with-arcpy)

    Parameter inputDataset: the layer / table to create a field map for
    Condition: a string describing a valid table in the ArcPy environment

    Parameter mappingDict: a collections of Key Values pairs to map
    Condition: is a dictionary containing {str: str} KVPs
    """
    fieldMappings = arcpy.FieldMappings()

    for sourceField in mappingDict:
        # st.loginfo(f"SourceField is {sourceField}")
        fMap = arcpy.FieldMap()
        fMap.addInputField(inputDataset, sourceField)
        outField = fMap.outputField
        outField.name = mappingDict[sourceField]
        outField.aliasName = mappingDict[sourceField]
        fMap.outputField = outField
        fieldMappings.addFieldMap(fMap)

    return fieldMappings


def field_dict_for_op(dis_layer):
    """
    Builds a mapping dictionary between a dissolve layer and the original

    Keys are the input fname, values are output fname. 

    It is deeply annoying that there's no flag to switch off this behavior
    in the builtin Dissolve tool.
    
    Should I probably do this in one function? Sure! 
    but fmapfordict was handed to me on a silver platter and I don't feel like
    refactoring...

    Parameter layer: the  layer created by the dissolve operation
    Conditions: a string describing a valid layer in the ArcPy environment
                layer described must have been created by a dissolve operation
    """
    ops = ["SUM",
           "MEAN", 
           "MIN", 
           "MAX", 
           "RANGE", 
           "STD", 
           "COUNT", 
           "FIRST",
           "LAST",
           "MEDIAN",
           "VARIANCE",
           "UNIQUE"
           "CONCATENATE"
           ]
    fnl = list_field_names(dis_layer)
    fm_dict = {}
    for fn in fnl:
        nfnt = fn.partition("_")
        if nfnt[0] in ops:
            nfn  = nfnt[2]
            #st.loginfo(f"Adding mapping for {fn} to {nfn}")
            fm_dict[fn] = nfn
    st.loginfo(pf(fm_dict))
    return fm_dict


def field_dict_for_op(dis_layer):
    """
    Builds a mapping dictionary between a dissolve layer and the original

    Keys are the input fname, values are output fname. 

    It is deeply annoying that there's no flag to switch off this behavior
    in the builtin Dissolve tool.
    
    Should I probably do this in one function? Sure! 
    but fmapfordict was handed to me on a silver platter and I don't feel like
    refactoring...

    Parameter layer: the  layer created by the dissolve operation
    Conditions: a string describing a valid layer in the ArcPy environment
                layer described must have been created by a dissolve operation
    """
    ops = ["SUM",
           "MEAN", 
           "MIN", 
           "MAX", 
           "RANGE", 
           "STD", 
           "COUNT", 
           "FIRST",
           "LAST",
           "MEDIAN",
           "VARIANCE",
           "UNIQUE"
           "CONCATENATE"
           ]
    fnl = list_field_names(dis_layer)
    fm_dict = {}
    for fn in fnl:
        nfnt = fn.partition("_")
        if nfnt[0] in ops:
            nfn  = nfnt[2]
            #st.loginfo(f"Adding mapping for {fn} to {nfn}")
            fm_dict[fn] = nfn
    st.loginfo(pf(fm_dict))
    return fm_dict


def dissolve_and_rectify(in_feature, solvent, out_feature):
    """
    Dissolves a selection, then removes the affix from the resultant output

    This function uses a ValueTable to create a dissolution, then produces
    a field map linking dissolved field names back to the original field names.
    
    For details on limitations, see documentation for 
        unionmerge.field_dict_for_op() and unionmerge.field_map_for_dict()

    Parameter in_feature: the input feature
    Condition: a string describing a valid layer in the ArcPy environment

    Parameter solvent: the ValueTable used to dissolve
    Condition: must be an ArcPy valuet table valid for use in arcmg.Dissolve

    Parameter out_feature: the output feature
    Condition: a string describing a layer to be created 
               in the ArcPy environment
    """
    arcmg.Dissolve(
        in_features= in_feature,
        out_feature_class=solution,
        dissolve_field=None,
        statistics_fields= solvent,
        multi_part="MULTI_PART",
        unsplit_lines="DISSOLVE_LINES",
        concatenation_separator=""
    )
    fdict = field_dict_for_op(solution)
    map = field_map_for_dict(solution, fdict)
    # ESRI 🤝 Hegel
    #       ⤷ arcane incomprehensible nonsense
    arcpy.conversion.ExportFeatures(solution, out_feature, field_mapping = map)
    arcmg.CalculateField(
        in_table=out_feature,
        field="IS_OUG",
        expression=1,
        expression_type="PYTHON3",
    )
    arcmg.CalculateField(
        in_table=out_feature,
        field="PROCESSOR",
        expression="'" + PROCESSOR_VERSION + "'",
        # Hideous. I love it.
        expression_type="PYTHON3",
    )
