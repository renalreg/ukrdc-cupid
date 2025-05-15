"""
Functions to add reusable types in the xsd to the models. Currently they are 
mostly either hardcoded or live at the location where they are used. Examples
of these are the address type, the clinician type or the common metadata type.
In future versions of the ukrdc I think these should all be their own tables in
the ukrdc and where possible should be picklists which are not updated by the 
xml (see the way ukrdc_ods_gp_codes is handled for example). The UKRRReftable 
models could be used to sort this out. 
"""
