#!/usr/bin/env python
import os
import xml.etree.ElementTree as ET

CF_STANDARD_NAME_FILE = 'data_sources/cf-standard-name-table.xml'
PROLOG_OUTPUT_FILE = 'output/cf_standard_name.pl'

PROLOG_STANDARD_NAME_FMT = "standardname([{}], '{}', '{}')."
FIX_UNICODE_ERROR = True


def extract_prolog_standard_names(cf_standard_name_table):
    """Extract list of prolog_standard_names from cf_standard_name_table
    
    cf_standard_name_table should be a cf-standard-name-table.xml file."""
    prolog_standard_names = []
    tree = ET.parse(cf_standard_name_table)
    root = tree.getroot()

    # Loop over all entries.
    for entry in root.findall('entry'):
        # Get the id attrib.
        prolog_name = entry.attrib['id'].replace('_', ',')

        # Handle special case of 1D in name.
        if entry.attrib['id'] == 'photolysis_rate_of_ozone_to_1D_oxygen_atom':
            prolog_name = prolog_name.replace("1D", "'1D'")

        # Get extra info.
        canonical_units = entry.find('canonical_units').text
        description = entry.find('description').text
        if FIX_UNICODE_ERROR and description:
            description = description.replace(u"\u2019", "")

        try:
            prolog_standard_name = PROLOG_STANDARD_NAME_FMT.format(prolog_name, 
                                                                   canonical_units,
                                                                   description)
            prolog_standard_names.append(prolog_standard_name)
        except Exception as e:
            # Original cf-standard-name-table has dodgy unicode char in SST entry.
            # This will show up without the FIX_UNICODE_ERROR option.
            print('Cannot make entry for {}'.format(entry.attrib['id']))
            print(e)
    return prolog_standard_names


if __name__ == '__main__':
    prolog_standard_names = extract_prolog_standard_names(CF_STANDARD_NAME_FILE)

    # Make output dir if it doesn't exist.
    if not os.path.exists(os.path.dirname(PROLOG_OUTPUT_FILE)):
        os.makedirs(os.path.dirname(PROLOG_OUTPUT_FILE))

    # Write out standard names.
    with open(PROLOG_OUTPUT_FILE, 'w') as f:
        for prolog_standard_name in prolog_standard_names:
            f.write(prolog_standard_name + '\n')

    print('Written to {}'.format(PROLOG_OUTPUT_FILE))
