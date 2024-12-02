# Single member od graphql federation

## Dependency

Depends on GQL_UG endpoint.
To enable running, uois stack must be deployed.
See https://github.com/hrbolek/_uois

To enable interaction with webinterface, log in webinterface in uois.
See http://localhost:33001/

Be sure that you use webinterface on http://localohost:8001/gql.
Do not use http://127.0.0.1/gql

## State of the Art

Tables are defined in way which allows to work with dbrows as with dataclasses.
This enables conversion into dict structures and use them in GQLModel init.
It is propably the shortest conversion from dbrow into GQLModel.


## Keypoints

For authentization is used WhoAmIExtension which sends a query to gql_ug. 
With this query, roles of logged user are revealed and stored into context.
This is very usefull for resolving permissions defined by rolename.

## Usefull commands

```bash
uvicorn main:app --env-file environment.txt --port 8001
```

```bash
pytest --cov-report term-missing --cov=src --log-cli-level=INFO -x
```

## Some prompts for chatgpt

```chatgpt
convert next python code into mapped class (SQLAlchemy) with use of mapped_column and properly annotate it, do not include type in mapped_column and also do not use Optional typing in annotation, instead add parameter nullable=True
```