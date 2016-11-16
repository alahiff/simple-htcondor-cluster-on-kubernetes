# A simple HTCondor cluster on Kubernetes
## Setting up the cluster
Create a random pool password with name `password` in the `/tmp` directory:
```
docker run -it -v /tmp:/vol alahiff/htcondor-generate-password:latest
```
This will create a file `/tmp/password`. Create a secret from this new pool password:
```
kubectl create secret generic htcondor-pool-password --from-file=/tmp/password
```
