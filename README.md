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
Try killing the central manager:
```
# kubectl delete pod htcondor-central-manager-2538661822-1q8pl
pod "htcondor-central-manager-2538661822-1q8pl" deleted
```
A new central manager pod will automatically be created:
```
# kubectl get deployments,pods
NAME                              DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deploy/htcondor-central-manager   1         1         1            0           18h
deploy/htcondor-schedd            1         1         1            1           16h
deploy/htcondor-worker            2         2         2            2           16h

NAME                                           READY     STATUS              RESTARTS   AGE
po/htcondor-central-manager-2538661822-1q8pl   1/1       Terminating         0          18h
po/htcondor-central-manager-2538661822-g3ngm   0/1       ContainerCreating   0          5s
po/htcondor-schedd-308862252-r6xkj             1/1       Running             0          16h
po/htcondor-worker-123133369-lc41z             1/1       Running             0          30m
po/htcondor-worker-123133369-tdb70             1/1       Running             0          16h
```
Initially the new central manager won't know about the schedd or worker nodes:
```
# kubectl exec htcondor-central-manager-2538661822-g3ngm -i -t -- condor_status -any
MyType             TargetType         Name

Collector          None               My Pool - htcondor-central-manager-253866
DaemonMaster       None               htcondor-central-manager-2538661822-g3ngm
Negotiator         None               htcondor-central-manager-2538661822-g3ngm
```
but after a while the schedd and worker node(s) will update the new central manager:
```
# kubectl exec htcondor-central-manager-2538661822-g3ngm -i -t -- condor_status -any
MyType             TargetType         Name

Collector          None               My Pool - htcondor-central-manager-253866
DaemonMaster       None               htcondor-central-manager-2538661822-g3ngm
Negotiator         None               htcondor-central-manager-2538661822-g3ngm
Scheduler          None               htcondor-schedd-308862252-r6xkj
DaemonMaster       None               htcondor-schedd-308862252-r6xkj
DaemonMaster       None               htcondor-worker-123133369-lc41z
Machine            Job                slot1@htcondor-worker-123133369-lc41z
Machine            Job                slot2@htcondor-worker-123133369-lc41z
DaemonMaster       None               htcondor-worker-123133369-tdb70
Machine            Job                slot1@htcondor-worker-123133369-tdb70
Machine            Job                slot2@htcondor-worker-123133369-tdb70
```

## Separated collector and negotiator
Instead of having a single central manager pod, consisting of both a collector and negotiator, we can separate the central manager into two pods. After creating a pool password as descibed above, we firstly create a service for the collector, then create deployments for the collector and negotiator pods:
```
kubectl create -f v2/htcondor-collector-service.yaml
kubectl create -f v2/htcondor-collector-deployment.yaml
kubectl create -f v2/htcondor-negotiator-deployment.yaml
```
Now create a schedd and worker node:
```
kubectl create -f  v2/htcondor-schedd-deployment.yaml
kubectl create -f  v2/htcondor-worker-deployment.yaml
```
You should see
```
kubectl get deployments,pods
NAME                         DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deploy/htcondor-collector    1         1         1            1           1h
deploy/htcondor-negotiator   1         1         1            1           1h
deploy/htcondor-schedd       1         1         1            1           1h
deploy/htcondor-worker       1         1         1            1           1h

NAME                                      READY     STATUS    RESTARTS   AGE
po/htcondor-collector-4216735924-d9nq5    1/1       Running   0          1h
po/htcondor-negotiator-1710181096-1stkb   1/1       Running   0          1h
po/htcondor-schedd-1411924804-9sdqr       1/1       Running   0          1h
po/htcondor-worker-706141080-z5qld        1/1       Running   0          1h
```
Note that there is no point scaling the number of collector pods with the configuration in use (this won't help with scaling or redundancy).

We can also check that all the expected HTCondor daemons are running:
```
kubectl exec htcondor-collector-4216735924-d9nq5 -i -t -- condor_status -any
MyType             TargetType         Name

Collector          None               My Pool - htcondor-collector-4216735924-d
DaemonMaster       None               htcondor-collector-4216735924-d9nq5
Negotiator         None               NEGOTIATOR
DaemonMaster       None               htcondor-negotiator-1710181096-1stkb
Scheduler          None               htcondor-schedd-1411924804-9sdqr
DaemonMaster       None               htcondor-schedd-1411924804-9sdqr
DaemonMaster       None               htcondor-worker-706141080-z5qld
Machine            Job                slot1@htcondor-worker-706141080-z5qld
Accounting         none               <none>
```

## Autoscaling the number of worker nodes
A simple way to do this would be to use a horizontal pod autoscaler. The major problem with this is that downscaling will quite possibly result in worker nodes which are doing useful work being killed. As an alternative, one option is to use a custom controller pod which creates worker node pods as they are needed, i.e. depending on how many idle jobs there are. If the worker node pod is configured to only start new jobs for a limited time period and to exit after being idle for specified time, downscaling will occur naturally.

Firstly, create a ConfigMap containing the worker node pod template:
```
kubectl create configmap htcondor-worker-pod-template --from-file=htcondor-worker.json
```
If RBAC authorization is enabled, we need to ensure that the controller pod has the appropriate permissions:
```
kubectl create -f serviceaccount-creator.yaml
kubectl create -f role-pods.yaml
kubectl create rolebinding pods-creator --clusterrole=pods-creator --serviceaccount=default:pod-creator --namespace=default
```
Now we need to run the HTCondor pool controller pod. If RBAC is enabled run the following:
```
kubectl create -f htcondor-pool-deployment-rbac.yaml
```
or if not:
```
kubectl create -f htcondor-pool-deployment.yaml
```
