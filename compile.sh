#!/usr/bin/env bash

# Default PREFIX value
PREFIX_DEFAULT=/usr/local

#######################################
# All of our Makefile options
#######################################

# Selects the install prefix directory
PREFIX=$1

if [ -z "$PREFIX" ]; then
    echo "\"PREFIX\" variable unset. Default it to \""${PREFIX_DEFAULT}"\""
    PREFIX=${PREFIX_DEFAULT}
fi

COMMAND_CLIENT="\
    make PREFIX=${PREFIX} && \
    sudo make PREFIX=${PREFIX} install"

COMMAND_ARRAY=(
    "${COMMAND_CLIENT}"
)

for i in "${COMMAND_ARRAY[@]}"
do
    echo "Executing: " $i
    eval $i

    # Check return value
    rc=$?
    if [[ $rc != 0 ]]; then
        exit $rc
    fi
done
