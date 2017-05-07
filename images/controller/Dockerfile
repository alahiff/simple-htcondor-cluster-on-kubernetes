FROM centos:7

# Dependencies
RUN yum -y install wget python-requests

# Install yum repository
RUN cd /etc/yum.repos.d && wget http://research.cs.wisc.edu/htcondor/yum/repo.d/htcondor-stable-rhel7.repo

# Import signing key
RUN wget http://research.cs.wisc.edu/htcondor/yum/RPM-GPG-KEY-HTCondor && rpm --import RPM-GPG-KEY-HTCondor

# Install HTCondor
RUN yum -y install condor condor-python

COPY condor_config.local /etc/condor/
COPY htcondor-pool.py /

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
