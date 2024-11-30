import sqlalchemy
import datetime

from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    DateTime,
    ForeignKey,
    Sequence,
    Table,
    Boolean,
    Uuid
)
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from typing import Optional

def newUuidAsString():
    return f"{uuid.uuid4()}"


def UUIDFKey(comment=None, nullable=True, **kwargs):
    return Column(Uuid, index=True, comment=comment, nullable=nullable, **kwargs)

def UUIDColumn():
    return Column(Uuid, primary_key=True, comment="primary key", default=uuid.uuid4)

###########################################################################################################################
#
# zde definujte sve SQLAlchemy modely
# je-li treba, muzete definovat modely obsahujici jen id polozku, na ktere se budete odkazovat
#


class BaseModel(MappedAsDataclass, DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(index=True, primary_key=True, default_factory=uuid.uuid4)

    created: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True, server_default=sqlalchemy.sql.func.now())
    lastchange: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True, server_default=sqlalchemy.sql.func.now())

    createdby_id: Mapped[uuid.UUID] = mapped_column(default=None, nullable=True)#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby_id: Mapped[uuid.UUID] = mapped_column(default=None, nullable=True)#Column(ForeignKey("users.id"), index=True, nullable=True)
    rbacobject_id: Mapped[uuid.UUID] = mapped_column(default=None, nullable=True, comment="id rbacobject")#Column(ForeignKey("users.id"), index=True, nullable=True)
###
