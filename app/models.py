from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import Table, Column, ForeignKey, String, Date, Float, Integer, UniqueConstraint
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

class TicketInventory(Base):
    __tablename__ = "ticket_inventory"
    
    __table_args__ = (
        UniqueConstraint("ticket_id", "inventory_id", name="uq_ticket_inventory_ticket_inventory"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    ticket: Mapped["Ticket"] = relationship(back_populates="ticket_inventory_items")
    inventory_item: Mapped["Inventory"] = relationship(back_populates="ticket_inventory_items")

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
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
    ticket_inventory_items: Mapped[List["TicketInventory"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan"
    )
       
class Inventory(Base):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    ticket_inventory_items: Mapped[List["TicketInventory"]] = relationship(
        back_populates="inventory_item",
        cascade="all, delete-orphan"
    )
    
class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(255), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    
    tickets: Mapped[List["Ticket"]] = relationship(secondary=ticket_mechanic_joint_table, back_populates="mechanics")
    