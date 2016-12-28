#!/bin/sh

# Configuration
echo "SEC_PASSWORD_FILE = $SEC_PASSWORD_FILE" >> /etc/condor/config.d/docker

# Run HTCondor
/usr/sbin/condor_master -f
