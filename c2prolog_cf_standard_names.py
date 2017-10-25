#!/usr/bin/env python
import os
import urllib2
import xml.etree.ElementTree as ET

CF_STANDARD_NAME_URL_FMT = 'http://cfconventions.org/Data/cf-standard-names/{}/src/cf-standard-name-table.xml'
CF_STANDARD_NAME_FILE_FMT = 'data_sources/cf-standard-name-table.v{}.xml'
CF_VERSION = 47

PROLOG_OUTPUT_FILE_FMT = 'output/cf_standard_name.v{}.pl'

PROLOG_STANDARD_NAME_FMT = "standardname([{}], '{}', '{}')."
FIX_UNICODE_ERROR = True


def get_standard_names_xml(version, cf_standard_name_table):
    print('Getting CF standard name table version {}'.format(version))
    url = CF_STANDARD_NAME_URL_FMT.format(version)
    print('  from: {}'.format(url))
    resp = urllib2.urlopen(url)
    with open(cf_standard_name_table, 'w') as f:
        print('  saving to: {}'.format(cf_standard_name_table))
        f.write(resp.read())

def extract_prolog_standard_names(cf_standard_name_table):
    """Extract list of prolog_standard_names from cf_standard_name_table
    
    cf_standard_name_table should be a cf-standard-name-table.xml file."""
    print('Reading from: {}'.format(cf_standard_name_table))
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
            print('ERROR: Cannot make entry for {}'.format(entry.attrib['id']))
            print(e)
    return prolog_standard_names


if __name__ == '__main__':
    print('Using CF version {}'.format(CF_VERSION))
    cf_standard_name_table = CF_STANDARD_NAME_FILE_FMT.format(CF_VERSION)
    prolog_output_file = PROLOG_OUTPUT_FILE_FMT.format(CF_VERSION)

    # Make stansard name file dir if it doesn't exist.
    if not os.path.exists(os.path.dirname(cf_standard_name_table)):
        os.makedirs(os.path.dirname(cf_standard_name_table))

    # Make output dir if it doesn't exist.
    if not os.path.exists(os.path.dirname(prolog_output_file)):
        os.makedirs(os.path.dirname(prolog_output_file))

    if not os.path.exists(cf_standard_name_table):
        get_standard_names_xml(CF_VERSION, cf_standard_name_table)
    prolog_standard_names = extract_prolog_standard_names(cf_standard_name_table)

    # Write out standard names.
    with open(prolog_output_file, 'w') as f:
        for prolog_standard_name in prolog_standard_names:
            f.write(prolog_standard_name + '\n')

    print('Written to {}'.format(prolog_output_file))
