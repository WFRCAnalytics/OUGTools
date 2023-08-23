# OUGTools
*Lilah Rosenfield // WFRC*

 A set of tools to merge individually owned units into Owned Unit Groupings in a Parcel Dataset. Requires an ArcGIS Pro Advanced License.

## Step 0: Quickstart
This tool should run out of the box, with basic explanations of functions and requirement for parameters outlined within the toolbox. You can feel free to simply download a zip, extract it to a folder, and open the toolbox within your project. If you're wondering if this tool can serve your needs, aren't sure what an OUG is, or want some help understanding how this whole thing works, read on!

## Step 1: So you want to identify new residential units
Here at WFRC, we Here at WFRC, we maintain a variety of datasets and models intended to support our work guiding and supporting the future of transportation and development along the Wasatch Front.

One such dataset is the [Housing Unit Inventory](https://gis.utah.gov/data/planning/housing-unit-inventory/). This dataset is derived from the existing assessor LIR dataset, but includes modifications and derived values to help us, our partners and members of the community understand evolving housing patterns.

One such modification we make when producing this inventory is merging certain parcels into what we call *Owned Unit Groupings* or OUGs.

### The What?

You see, assessors are responsible primarily for identifying taxable property, and while the data they produce is quite useful for other purposes, it is still primarily created for that role. This means that *each independently owned unit* needs to have its own feature. This works fine for single-family residential units and for apartments owned by a single entity, but for multi-family dwellings, *especially* mid-rise and high-rise condominiums, this poses a challenge for representation on a two-dimensional map.

For assessors, this issue is typically resolved assigning individually owned units to features with entirely or partially fictive geometries within the true geometry of the parcel owned by the HOA, collaborative governance structure, or developer (we'll call this big parcel the **Common Parcel** or **CmP**, and the smaller, potentially geometrically fictive parcels the **Unit Parcels** or **UnP**). Typically it looks something like this.

<p align="center">
    <img src="./Condo.png" alt="An image showing a mid-rise condo as seen in an assessor's parcel map. It shows that, nested within the parcel surrounding the building, there are a variety of smaller parcels that do not correspond with anything physical. There are two separate 'stacks' of rectangular features. Each of rectangles within the right stack further contain a varying number of circular features, mostly, but not entirely contained within said rectangles.">
    <br>
    ew.
</p>
The thing is, for our purposes, we don't actually care about who owns specific parcels, and we'd like to be able to make direct comparisons between, for example, multi-family condos and apartments. Enter,the Owned Unit Grouping (or OUG). This is, most simply, a version of the Common Parcel that incorporates certain information from the Unit Parcels within it.

## Part 2: That's just a dissolve, right?
At its most basic, yes. This is just a dissolve between the Common Parcels and the Unit Parcels. But right away we face some issues. I was working to *update* the dataset, which means the preprocessing we'd done had eliminated unmodified parcels, including some Common Parcels I needed to merge. Said parcels were still present in the overall LIR Dataset, but dissolve only works if every feature is on the same layer. Additionally, because of the number of edge cases that were likely to emerge, I felt it was important to work through each OUG one-by-one so I could identify issues as they arose.

Instead of going through a multi-step process of manual selection, appending the wider parcel, and then dissolving for all 6000 newly built units, I decided that it'd be better to simply build out a tool that allowed me to select a CmP and run all relevant processes. Enter...

## Part 3: The Parcel Review Toolbox
ArcGIS provides a number of excellent tools for scripting. After playing around with a couple of different options, I eventually settled on scripting a [script tool](https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/a-quick-tour-of-creating-script-tools.htm) with Python operating on an ArcToolbox. The results of this adventure are the collection of scripts and the toolbox located in this repository . 

## Part N: Future Steps
I made this tool during an internship with WFRC's excellent analytics group, and have left it in their capable hands. That said, there are potentially some changes that I would have loved to make. 

First off (and perhaps most obviously), if I'd needed to work with tens of thousands rather than thousands of parcels, it may have been worth it to figure out a way to automate the identification of parcels that need to be OUG'd, such that the tool could be run once per county. If someone at another MPO or other organization that works with parcel data figures out a way to do so consistently, feel free to put in a PR!

 Also: this tool requires an ArcGIS Pro Advanced license to run the Eliminate Polygon Part tool, if you can figure out a drop-in replacement for this tool, or another way to perform the equivalent function, also drop a pull request!