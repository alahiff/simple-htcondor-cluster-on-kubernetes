#!/bin/sh
htcpass=`uuidgen`
condor_store_cred -p $htcpass -f /vol/password
chmod a+r /vol/password
