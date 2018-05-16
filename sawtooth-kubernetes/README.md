## Build deployments kubernetes

```sh
ssh -o StrictHostKeyChecking=no root@1.tcp.ap.ngrok.io -p 20086
```
password: 1qazXSW@

```sh
cd /home/node/sawtooth-kubernetes
```
Using Environment A (envA)

```sh
./command/remove-2-validators.sh (only use this command if you run envB before)
kubectl apply -f optimized-sawtooth/kubernetes-envA
```
Using Environment B (envB)

```sh
./command/add-2-validators-again.sh (only use this command if you run envA before)
kubectl apply -f optimized-sawtooth/kubernetes-envB
```
Do the same above steps with vanilla sawtooth in folder vanilla-sawtooth

### Check the status of kubernetes

Apply this url:

```sh
https://sawtooth.ap.ngrok.io/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/node?namespace=_all
```

Check the "token" option and copy this below token to authorize (please wait about 4-5 seconds depending on the internet):

```sh
eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLTY0cWRuIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJhYjM0MTkwNC01NzMzLTExZTgtYTczOC1kNDg1NjQ5YTdlMDciLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06YWRtaW4tdXNlciJ9.kiAN7x4i8kcfyLaNjPr2eivRDy6kIIkHmFcbbJZdOvaUGT79TGL4wR_3HYtW1_9pOz2numpCGNjhAFkxldtkHIRIk1hLUP0cqJ8i6LMsOStifuOP_RxQgc_KFPRkFzRUXcn3iSoaPW8ZXL6p6zlnaCeKXN-QBy77s01DJCrOWcMJ7qPniprFaALidyub5wED-Dqi0WzwmheYYXNSOY-A3iovsTX-gUWRe33WGRNAQAVduxMuyY3nl6tZSWpBPySgD8tUvWC0R5xvLajEbFwBqmhBn19-vOwsgHwdaeILFF_clTqjqrHVRcH0EiKIQ3xlFCbn7FfAvpQcdWsOcBvUrA
```


### Run test & benchmark

Assume that you are in /home/node in the server via ssh

```sh
cd sawtooth-caliper/
yarn test-both-1 (use this command if you want to benchmark envA)
yarn test-both-3 (use this command if you want to benchmark envB)
```

To change the pressure of input transaction, we modify the property called "txNumber" and "tps"
in 2 files: benchmark/simple/config.json (for envA) and benchmark/simple/config-3.json (for envB)

To change the number of transactions in a batch, we modify the number "100" to your number at the line 46 in the file: src/sawtooth/sawtooth.js
