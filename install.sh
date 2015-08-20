#!/bin/bash
## INFO ##
## INFO ##

# TODO: **version checking**
#       Check versions of the given packages not only availability

# Check if `dagger` dependency installed
python3 -c "from dagger.graph import Graph" &> /dev/null;
# If not installed
if [ $? -ne 0 ];
then
    # Download and install it
    printf "Dependency not found: 'dagger'\n";
    printf "Downloading and installing: 'dagger'\n";
    mkdir -p dependencies;
    cd dependencies;
    git clone https://github.com/petervaro/dagger;
    cd dagger;
    sudo python3 setup.py install;
    cd ../../;
# If installed
else
    printf "Dependency found: 'dagger'\n";
fi;


# Check if `orderedset` dependency installed
python3 -c "from orderedset import OrderedSet" &> /dev/null;
# If not installed
if [ $? -ne 0 ];
then
    # Download and install it
    printf "Dependency not found: 'orderedset'\n";
    printf "Downloading and installing: 'orderedset'\n";
    mkdir -p dependencies;
    cd dependencies;
    git clone https://github.com/petervaro/orderedset;
    cd orderedset;
    sudo python3 setup.py install;
    cd ../../;
# If installed
else
    printf "Dependency found: 'orderedset'\n";
fi;


# Remove 'dependencies' directory if present
rm -Rf dependencies;


# Install argon
printf "Installing argon...\n";
sudo python3 setup.py install;
exit;
