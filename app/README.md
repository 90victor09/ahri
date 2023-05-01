
```shell
kubectl create namespace ahri

helm upgrade --install -n ahri -f helm-values/ahri.yaml \
 ahri ./helm \
 --set "db.host=$DB_HOST,db.port=$DB_PORT,db.db=$DB_DB,db.user=$DB_USER,db.pass=$DB_PASS,apiKey=$APP_API_KEY"
```
