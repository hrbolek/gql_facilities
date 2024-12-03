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

```chatpgpt
consider this as input
@strawberry.field(description="""Updates an author""")
async def publication_author_update(
    self, info: strawberry.types.Info, author: PublicationAuthorUpdateGQLModel) -> "AuthorResultGQLModel":
    return await encapsulateUpdate(info, PublicationAuthorGQLModel.getLoader(info), author, PublicationAuthorResultGQLModel(id=author.id, msg="ok"))

next part is output

@strawberry.field(description="""Updates an author""")
async def publication_author_update(
    self, info: strawberry.types.Info, author: PublicationAuthorUpdateGQLModel) -> typing.Union["AuthorGQLModel", InsertError["AuthorGQLModel"]]:
    return await Insert[AuthorGQLModel].DoItSafeWay(info=info, entity=author)

change by same way this pay some attention to replace Insert (insert), Update (update), Delete (delete), if you include Insert in funcion body, the result must contain InsertError, similary for other cases

@strawberry.field(description="""Adds the authorship to the publication, Currently it does not check if the authorship exists.""")
async def publication_author_insert(
    self, info: strawberry.types.Info, author: PublicationAuthorInsertGQLModel) -> "AuthorResultGQLModel":
    return await encapsulateInsert(info, PublicationAuthorGQLModel.getLoader(info), author, PublicationAuthorResultGQLModel(id=author.id, msg="ok"))

```

```chatgpt
I want to generate CUD mutations / decorated function for a particular type named
ModelGQLName

in such case I want the reaponse from you which will be
@strawberry.field(
    description="""Inserts a medal""",
    permission_classes=[
        OnlyForAuthentized
    ])
async def medal_update(
    self, info: strawberry.types.Info, medal: MedalInsertGQLModel) -> typing.Union["MedalGQLModel", InsertError["MedalGQLModel"]]:
    return await Insert[MedalGQLModel].DoItSafeWay(info=info, entity=author)

@strawberry.field(
    description="""Updates the medal""",
    permission_classes=[
        OnlyForAuthentized
    ])
async def medal_update(
    self, info: strawberry.types.Info, medal: MedalUpdateGQLModel) -> typing.Union["MedalGQLModel", UpdateError["MedalGQLModel"]]:
    return await Update[MedalGQLModel].DoItSafeWay(info=info, entity=author)

@strawberry.field(
    description="""Delete the medal""",
    permission_classes=[
        OnlyForAuthentized
    ]
    )
async def medal_delete(
    self, info: strawberry.types.Info, medal: MedalUpdateGQLModel) -> typing.Optional[UpdateError["MedalGQLModel"]]:
    return await Update[MedalGQLModel].DoItSafeWay(info=info, entity=author)

do it now for RankGQLModel
```

```chatpgpt
convert next python code into mapped class (SQLAlchemy) with use of mapped_column and properly annotate it, do not include type in mapped_column and also do not use Optional typing in annotation, instead add parameter nullable=True
class StateTransitionModel(BaseModel):
    __tablename__ = "statetransitions"

    id = UUIDColumn()
    name = Column(String, comment="name of state transition")
    name_en = Column(String, comment="english name of state transition")

    source_id = Column(ForeignKey("states.id"), index=True, nullable=False)
    target_id = Column(ForeignKey("states.id"), index=True, nullable=False)
    statemachine_id = Column(ForeignKey("statemachines.id"), index=True, nullable=False)
```