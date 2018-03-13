#! /bin/bash

set -e
set -x

function service_is_running() {
    sudo -u patient -i systemctl --user is-active 'gwn-phone.service'
}



function scrape_logs() {
    journalctl >"${ADT_ARTIFACTS}/journal.txt"
}

trap scrape_logs EXIT



systemctl restart gwn-seed-patient.service
# It is unclear when `systemctl` is and is not blocking. If the call to seed /home/patient is non-blocking
# then there is a theoretical race condition here where nodm will start running at a point in time when not
# all of the necessary config files are present in /home/patient.
#
# The consequence of this is that strange errors will occur that look like missing configuration files, and
# when the developer digs in to see if the config files are missing, they will be present. If this is the case
# then an intelligent wait loop with a reasonable timeout will need to be implemented to guarantee completion
# of gwn-seed-patient.service
systemctl restart patientx.target



if ! service_is_running ; then
    deadline="$( date +%s )"
    let 'deadline+=60'

    while [[ "$( date +%s )" -le "${deadline}" ]] ; do
        if service_is_running ; then
            break
        else
            sleep 2
        fi
    done

    # let `set -e` bail us out if we exited the loop gracefully instead of via `break`, that is: the deadline expired.
    service_is_running
fi


# `adt-run` puts us in a copy of the project source tree, somewhere under /tmp inside the VM
# but `sudo -i` will cd to /home/patient, so we'll need to fully qualify the path to tests/integration
staging_directory="$( pwd )"
sudo -u patient -i env ADT_ARTIFACTS="${ADT_ARTIFACTS}" DISPLAY=:0 py.test-3 -v -ra --junit-xml=$ADT_ARTIFACTS/integration.xml "${staging_directory}"/tests/integration

