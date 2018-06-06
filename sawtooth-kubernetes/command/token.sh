token_name=admin-user
token_check=$(kubectl -n kube-system get secret | grep ${token_name}-token | awk '{print $1}')
if [[ -z $token_check ]];then
echo "Creating new one..."
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: $token_name
  namespace: kube-system
EOF

    cat <<EOF | kubectl create -f -
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: $token_name
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: $token_name
  namespace: kube-system
EOF

  echo "Patching dashboard to use nodePort 30000"
  kubectl patch service kubernetes-dashboard -n kube-system -p '{"spec":{"type":"NodePort","ports":[{"nodePort":30000,"port":443,"protocol":"TCP","targetPort":8443}]}}'
  token_check=$(kubectl -n kube-system get secret | grep ${token_name}-token | awk '{print $1}')
fi

if [[ ! -z $token_check ]];then
  echo "Your token: $token_check"
  echo
  kubectl -n kube-system describe secret $token_check | awk '$1~/token/{print $2}'
  # printCommand "kubectl -n kube-system describe secret $token_check | awk '$1~/token/{print $2}'"
  echo
else
  echo "Not found ${token_name}-token"
fi