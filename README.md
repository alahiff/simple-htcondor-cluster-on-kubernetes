# A simple HTCondor cluster on Kubernetes
## Setting up the cluster
### Preparing the pool password
We will use a pool password (i.e. shared secret) to secure the HTCondor cluster. Create a random pool password with filename `password` in the `/tmp` directory:
```
docker run -it -v /tmp:/vol alahiff/htcondor-generate-password:latest
```
This will create a file `/tmp/password`. Create a secret from this new pool password:
```
kubectl create secret generic htcondor-pool-password --from-file=/tmp/password
```
### Deploy the central manager, schedd and a worker node
Firstly deploy the central manager:
```
kubectl create -f htcondor-central-manager-service.yaml
kubectl create -f htcondor-central-manager-deployment.yaml
```
Once the central manager is running, i.e.
```
# kubectl get deployment htcondor-central-manager
NAME                       DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
htcondor-central-manager   1         1         1            1           17h
```
deploy the schedd and worker node:
```
kubectl create -f htcondor-schedd-deployment.yaml
kubectl create -f htcondor-worker-deployment.yaml
```
After a little while you should see 3 running pods:
```
# kubectl get pods
NAME                                        READY     STATUS    RESTARTS   AGE
htcondor-central-manager-2538661822-1q8pl   1/1       Running   0          17h
htcondor-schedd-308862252-r6xkj             1/1       Running   0          16h
htcondor-worker-123133369-tdb70             1/1       Running   0          16h
```
## Next steps
Check that all HTCondor components (collector, negotiator, schedd, and startd) are working correctly:
```
# kubectl exec htcondor-central-manager-2538661822-1q8pl -i -t -- condor_status -any
MyType             TargetType         Name

Collector          None               My Pool - htcondor-central-manager-253866
DaemonMaster       None               htcondor-central-manager-2538661822-1q8pl
Negotiator         None               htcondor-central-manager-2538661822-1q8pl
Scheduler          None               htcondor-schedd-308862252-r6xkj
DaemonMaster       None               htcondor-schedd-308862252-r6xkj
DaemonMaster       None               htcondor-worker-123133369-tdb70
Machine            Job                slot1@htcondor-worker-123133369-tdb70
Machine            Job                slot2@htcondor-worker-123133369-tdb70
```
Try scaling the number of worker nodes, e.g.
```
# kubectl scale --replicas 2 deployment/htcondor-worker
deployment "htcondor-worker" scaled
```
You should then see that there are 2 worker nodes:
```
# kubectl exec htcondor-central-manager-2538661822-1q8pl -i -t -- condor_status
Name               OpSys      Arch   State     Activity LoadAv Mem   ActvtyTime

slot1@htcondor-wor LINUX      X86_64 Unclaimed Idle      0.710 1895  0+00:00:04
slot2@htcondor-wor LINUX      X86_64 Unclaimed Idle      0.000 1895  0+00:00:29
slot1@htcondor-wor LINUX      X86_64 Unclaimed Idle      0.000 1895  0+16:25:51
slot2@htcondor-wor LINUX      X86_64 Unclaimed Idle      0.000 1895  0+16:25:07
                     Machines Owner Claimed Unclaimed Matched Preempting

        X86_64/LINUX        4     0       0         4       0          0

               Total        4     0       0         4       0          0
```
