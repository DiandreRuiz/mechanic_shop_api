from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import Table, Column, ForeignKey, String, Date, Float
from typing import List
from datetime import date

# Declare a base class for our models (will store metadata)
class Base(DeclarativeBase):
    pass

ticket_mechanic_joint_table = Table(
    "ticket_mechanic",
    Base.metadata,
    Column("ticket_id", ForeignKey("tickets.id"), primary_key=True),
    Column("mechanic_id", ForeignKey("mechanics.id"), primary_key=True)
)

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=False)
    
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="customer")
    
    
class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    service_description: Mapped[str] = mapped_column(String(1000), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    
    customer: Mapped["Customer"] = relationship(back_populates="tickets")
    mechanics: Mapped[List["Mechanic"]] = relationship(secondary=ticket_mechanic_joint_table, back_populates="tickets")
    
class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    
    tickets: Mapped[List["Ticket"]] = relationship(secondary=ticket_mechanic_joint_table, back_populates="mechanics")