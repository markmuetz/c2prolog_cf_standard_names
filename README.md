get:
    git clone https://github.com/markmuetz/c2prolog_cf_standard_names

run:

    cd c2prolog_cf_standard_names

    # Get version 47 of CF standard names.
    ./get-standard-name-table.sh 47
    # Generate prolog standard names file.
    ./c2prolog_cf_standard_names.py
