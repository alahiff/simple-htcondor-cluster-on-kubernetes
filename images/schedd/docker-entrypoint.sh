#!/bin/sh

# Configuration
echo "CONDOR_HOST = $CONDOR_HOST" > /etc/condor/config.d/docker
echo "SEC_PASSWORD_FILE = $SEC_PASSWORD_FILE" >> /etc/condor/config.d/docker

# Run HTCondor
/usr/sbin/condor_master -f
