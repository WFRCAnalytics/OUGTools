# OUGTools
*Lilah Rosenfield // WFRC*

 A set of tools to merge individually owned units into Owned Unit Groupings in a Parcel Dataset

## Step 1: So you want to identify new residential units
Here at WFRC, we Here at WFRC, we maintain a variety of datasets and models intended to support our work guiding and supporting the future of transportation and development along the Wasatch Front.

One such dataset is the [Housing Unit Inventory](https://gis.utah.gov/data/planning/housing-unit-inventory/). This dataset is derived from the existing assessor LIR dataset, but includes modifications and derived values to help us, our partners and members of the community understand evolving housing patterns.

One such modification we make when producing this inventory is merging certain parcels into what we call *Owned Unit Groupings* or OUGs.

### The What?

You see, assessors are responsible primarily for identifying taxable property, and while the data they produce is quite useful for other purposes, it is still primarily created for that role. This means that *each independently owned unit* needs to have its own feature. This works fine for single-family residential units and for apartments owned by a single entity, but for multi-family dwellings, *especially* mid-rise and high-rise condominiums, this poses a challenge for representation on a two-dimensional map.

For assessors, this issue is typically resolved assigning individually owned units to features with entirely or partially fictive geometries within the true geometry of the parcel owned by the HOA, collaborative governance structure, or developer. Typically it looks something like this.

<p align="center">
    <img src="./Condo.png" alt="An image showing a midrise condo as seen in an assessor's parcel map. It shows that, nested within the parcel surrounding the building, there are a variety of smaller parcels that do not correspond with anything physical. There are two separate 'stacks' of rectangular features. Each of rectangles within the right stack further contain a varying number of circular features, mostly, but not entirely contained within said rectangles.">
    <br>
    ew.
</p>
The thing is, for our purposes, we don't actually care about who owns specific parcels, and we'd like to be able to make direct comparisons between, for example, multi-family condos and apartments. Enter,the Owned Unit Grouping (or OUG). This is, most simply, a version of the containing feature but with a field specifically identifying