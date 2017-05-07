#!/usr/bin/python
import classad
import htcondor
import json, os, requests

def getIdleJobs():
    coll = htcondor.Collector()
    results = coll.query(htcondor.AdTypes.Schedd, 'true', ['Name'])

    idleJobs = 0
    for result in results:
        host = result['Name']
        scheddAd = coll.locate(htcondor.DaemonTypes.Schedd, host)
        schedd = htcondor.Schedd(scheddAd)

        jobs = schedd.query('', ['JobStatus'])
        for job in jobs:
            if job['JobStatus'] == 1:
                idleJobs += 1

    return idleJobs

def getNumPods(labelSelector):
    try:
        r = requests.get('http://127.0.0.1:8001/api/v1/namespaces/default/pods?labelSelector=' + labelSelector)
    except:
        print 'Failed to get list of pods'
        exit(1)

    podsPending = 0
    podsRunning = 0

    if 'items' in r.json() and r.json()['items'] != None:
        for pod in r.json()['items']:
            if pod['status']['phase'] == 'Running':
                name = pod['metadata']['name']
                podsRunning += 1
            elif pod['status']['phase'] == 'Pending':
                podsPending += 1

    return (podsPending, podsRunning)

def createPods(num, template, name):
    print 'Creating',num,'pods'
    try:
        with open(template, 'r') as content:
            raw = content.read()
    except:
        print 'Failed to open pod template'
        exit(1)

    for i in range (0, num):
       pod = json.loads(raw)
       pod['metadata']['generateName'] = name + '-'
       try:
           r = requests.post('http://127.0.0.1:8001/api/v1/namespaces/default/pods', data = json.dumps(pod))
       except:
           print 'Failed to create pod'
       print '  - status = ',r.status_code

if __name__ == '__main__':
    time.sleep(10)

    labelSelector = os.environ['HTCONDOR_LABEL_SELECTOR']
    podTemplate = os.environ['HTCONDOR_POD_TEMPLATE']
    maxWorkers = int(os.environ['HTCONDOR_MAX_WORKERS'])
    cpusPerWorker = int(os.environ['HTCONDOR_CPUS_PER_WORKER'])
    maxWorkersPerCycle = int(os.environ['HTCONDOR_MAX_WORKERS_PER_CYCLE'])

    while True:
        # Get number of idle jobs
        numIdleJobs = getIdleJobs()

        # Get numbers of running & idle pods
        (numPendingPods, numRunningPods) = getNumPods(labelSelector)

        print datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Pending:',numPendingPods,'Running:',numRunningPods,'NumIdleJobs=',numIdleJobs

        # Estimate number of worker pods to create
        num = numIdleJobs/cpusPerWorker

        # Limit number of pods if necessary
        if num > maxWorkersPerCycle:
            num = maxWorkersPerCycle

        if numRunningPods + numPendingPods + num > maxWorkers:
            num = maxWorkers - numRunningPods - numPendingPods
            if num < 0:
                num = 0

        # If there are idle pods, don't create any more
        if numPendingPods > 0:
            num = 0

        # Create new pods if necessary
        if num > 0:
            createPods(num, podTemplate, os.environ['HTCONDOR_POD_NAME'])

        time.sleep(60)

exit(0)
