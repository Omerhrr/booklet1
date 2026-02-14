"""
HR and Payroll Models
Supports Nigerian statutory deductions (PAYE, Pension)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class PayFrequency(str, enum.Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"


class Employee(Base):
    """Employee model"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    employee_number = Column(String(50), nullable=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    hire_date = Column(DateTime(timezone=True), nullable=False)
    termination_date = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    payroll_config = relationship("PayrollConfig", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    payslips = relationship("Payslip", back_populates="employee", cascade="all, delete-orphan")
    
    __table_args__ = (
        # UniqueConstraint('tenant_id', 'email', name='uq_employee_email'),
        ()
    )


class PayrollConfig(Base):
    """Employee payroll configuration"""
    __tablename__ = "payroll_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    gross_salary = Column(Float, default=0)
    pay_frequency = Column(Enum(PayFrequency), default=PayFrequency.MONTHLY)
    
    # Nigerian statutory deductions
    paye_rate = Column(Float, nullable=True)  # PAYE tax rate
    pension_employee_rate = Column(Float, nullable=True)  # Employee pension (8%)
    pension_employer_rate = Column(Float, nullable=True)  # Employer pension (10%)
    
    # Allowances (JSON array)
    allowances = Column(JSON, nullable=True)
    
    # Deductions (JSON array)
    deductions = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="payroll_config")
    
    __table_args__ = (
        ()
    )


class Payslip(Base):
    """Payslip for each pay period"""
    __tablename__ = "payslips"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    pay_period_start = Column(DateTime(timezone=True), nullable=False)
    pay_period_end = Column(DateTime(timezone=True), nullable=False)
    pay_date = Column(DateTime(timezone=True), nullable=False)
    
    gross_pay = Column(Float, default=0)
    total_allowances = Column(Float, default=0)
    total_deductions = Column(Float, default=0)
    
    # Nigerian statutory
    paye_deduction = Column(Float, default=0)
    pension_employee = Column(Float, default=0)
    pension_employer = Column(Float, default=0)
    
    net_pay = Column(Float, default=0)
    
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="payslips")
    additions = relationship("PayslipAddition", back_populates="payslip", cascade="all, delete-orphan")
    deductions_rel = relationship("PayslipDeduction", back_populates="payslip", cascade="all, delete-orphan")
    
    __table_args__ = (
        # UniqueConstraint('employee_id', 'pay_period_start', 'pay_period_end', name='uq_payslip_period'),
        ()
    )


class PayslipAddition(Base):
    """Payslip additions (bonuses, allowances)"""
    __tablename__ = "payslip_additions"
    
    id = Column(Integer, primary_key=True, index=True)
    payslip_id = Column(Integer, ForeignKey("payslips.id", ondelete="CASCADE"), nullable=False)
    
    description = Column(String(255), nullable=False)
    amount = Column(Float, default=0)
    
    # Relationships
    payslip = relationship("Payslip", back_populates="additions")
    
    __table_args__ = (
        ()
    )


class PayslipDeduction(Base):
    """Payslip deductions"""
    __tablename__ = "payslip_deductions"
    
    id = Column(Integer, primary_key=True, index=True)
    payslip_id = Column(Integer, ForeignKey("payslips.id", ondelete="CASCADE"), nullable=False)
    
    description = Column(String(255), nullable=False)
    amount = Column(Float, default=0)
    
    # Relationships
    payslip = relationship("Payslip", back_populates="deductions_rel")
    
    __table_args__ = (
        ()
    )
