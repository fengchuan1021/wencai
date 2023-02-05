### install and iniproject

clone code repository:

```
git clone https://github.com/xxx.git
```

initproject after clone.(such as input db password,db name ,etc).

```
python manage.py initall
```



### start up server

```
python app.py
```

or

```
python -m uvicorn app:app --reload
```





### generate cotroller and shema from openapi.json:



```shell
python manage.py importopenapi 1.json
```

## graphql
### query get method:
url: /graphql/modelname{[column1,column2,...]}/[id]
example:

1. get all products:
 ```js
"/graphql/product"  
 ```

2. get first 20 products. include total number of products:
```js
 "/graphql/product?pagenum=1&pagesize=20&returntotal=1"  
```


3. not return total number of products,for optimize purpose:
```js
"/graphql/product?pagenum=1&pagesize=20" 
 ```

4. get only product_id,description columns:
``` js
 "/graphql/product{product_id,description}"  
 ```

5. get product_id,description and join it's variant get variant_id,variant_title:
```js
 "/graphql/product{product_id,description,variant{variant_id,variant_title}}"
 ```
6. get product_id,description and join it's variant get variant_id,variant_title then join variant_image:

```js
 "/graphql/product{product_id,description,variant{variant_id,variant_title,variant_image{image_url,image_alt}}}"
 ```
7. get product info which product_id equal 66:
```js
 "/graphql/product{product_id,description,variant{variant_id,variant_title,variant_image{image_url,image_alt}}}/66"
 ```
8. filter by product status=online,order by id desc:
```js
'/graphql/product?filter={"product.status":"online"}&orderby=id desc'
```

backend will automaticly check the permission.for example user is a merchant,and merchant_id=12
```sql
select from product where product_id=6 and merchant_id=12
select from product left join variant on product.product_id=variant.product_id where product.product_id=6 and merchant_id=12
```


### query post method:
url: /graphql
example:

get all products:
```
post /graphql
{
"query":"product"
}
```
get first 20 products. include total number of products:
```
post /graphql
{
"query":"product",
"pagenum":1,
"pagesize":20,
"returntotal":1
}
```

not return total number of products,for optimize purpose:
```
post /graphql
{
"query":"product",
"pagenum":1,
"pagesize":20
}
```

get only product_id,description columns:
```
post /graphql
{
"query":"product{product_id,description}",
"pagenum":1,
"pagesize":20
}
```
get product_id,description and join it's variant get variant_id,variant_title:
```
post /graphql
{
"query":"product{product_id,description,variant{variant_id,variant_title}}",
"pagenum":1,
"pagesize":20
}
```

get product_id,description and join it's variant get variant_id,variant_title then join variant_image:
```
post /graphql
{
"query":"product{product_id,description,variant{variant_id,variant_title,variant_image{image_url,image_alt}}}"
}
```

get product info which product_id equal 66:
```
post /graphql
{
"query":"product{product_id,description,variant{variant_id,variant_title,variant_image{image_url,image_alt}}}",
"filter":{
"product_id":66
}
}
```

filter by product status=online,order by id desc:
```
post /graphql
{
"query":"product{product_id,description,variant{variant_id,variant_title,variant_image{image_url,image_alt}}}",
"filter":{
"status":'online'
},
"orderby":"id desc"
}
```
backend will automaticly check the permission.for example user is a merchant,and merchant_id=12
```
select from product where product_id=6 and merchant_id=12
select from product left join variant on product.product_id=variant.product_id where product.product_id=6 and merchant_id=12
```

## add filter in url's query parameter

1. eq
filter={"product_id":16} or filter={"product_id__eq":16}
```sql
select * from product where product_id=16
```
2. in
filter={"product_id__in":[4,5,6]}
```sql
select * product from product where product_id in (4,5,6)
```

3. gte,gt,lt,lte
filter={"product_id__in":[4,5,6],"product_price__gt":32}
```sql
select * product from product where product_id in (4,5,6) and product_price>32
```



### some docker command to setup mysql,redis,rabbmitmq quickly.





docker run --network myapp --add-host=host.docker.internal:host-gateway --restart=always --log-opt max-size=10m --log-opt max-file=5 -d --name myredis -p 6379:6379 redis

docker run --network myapp --add-host=host.docker.internal:host-gateway --restart=always --log-opt max-size=10m --log-opt max-file=5 -d --name mymysql -p3306:3306 -e MYSQL_ROOT_PASSWORD=6zZjywcDt7AcI3oI -e MYSQL_DATABASE=XT  -v /mysqldata:/var/lib/mysql mysql:8 --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4

docker run --network myapp --add-host=host.docker.internal:host-gateway --restart=always --log-opt max-size=10m --log-opt max-file=5 -d --hostname my-rabbit --name myrabbit -e RABBITMQ_DEFAULT_USER=admin -e RABBITMQ_DEFAULT_PASS=admin -p5672:5672 -p15672:15672 rabbitmq:3-management

docker run --network myapp --add-host=host.docker.internal:host-gateway --restart=always --log-opt max-size=10m --log-opt max-file=5 -d --name elasticsearch  -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_HEAP_SIZE=1G" elasticsearch:7.17.8

docker run --network myapp --add-host=host.docker.internal:host-gateway --restart=always --log-opt max-size=10m --log-opt max-file=5 -d --name kibana  -p 5601:5601 kibana:8.2.3
###other command.
alembic revision --autogenerate -m "add root_cause table"
alembic upgrade head
mysql+pymsql://root:root@host.docker.internal/buildbot


### if you have Distributed tasks,start celery worker

```
celery -A celery_mainworker beat -S redbeat.RedBeatScheduler -l info
celery -A celery_mainworker worker -l info --concurrency=4
```

