"""Application-specific SQLAlchemy ORM models.

When creating a new application from the template, replace these models
with your own domain entities.  The generic framework only requires that
all models inherit from :class:`app.models.Base`.
"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class GroupModel(Base):
    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    parent_id: Mapped[str | None] = mapped_column(
        String(100), ForeignKey("groups.id"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)

    parent: Mapped["GroupModel | None"] = relationship(
        "GroupModel", remote_side=[id], lazy="selectin"
    )
    details: Mapped[list["DetailModel"]] = relationship(
        back_populates="group_rel", lazy="selectin"
    )


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(300), nullable=False, unique=True, index=True
    )

    details: Mapped[list["DetailModel"]] = relationship(
        back_populates="item_rel", lazy="selectin", cascade="all, delete-orphan"
    )


class DetailModel(Base):
    __tablename__ = "details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    group_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("groups.id"), nullable=False
    )

    item_rel: Mapped["ItemModel"] = relationship(
        back_populates="details", lazy="selectin"
    )
    group_rel: Mapped["GroupModel"] = relationship(
        back_populates="details", lazy="selectin"
    )
