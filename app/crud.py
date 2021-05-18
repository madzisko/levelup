from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from . import models


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return db.query(models.Supplier).all()


def get_supplier(db: Session, supplier_id: int):
    return (
        db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first()
    )


def get_product(db: Session, supplier_id: int):
    o = db.query(models.Product.ProductID,
                 models.Product.ProductName,
                 models.Category,
                 models.Product.Discontinued
                 ).join(models.Category).\
            join(models.Supplier).\
            filter(models.Supplier.SupplierID == supplier_id).\
            order_by(models.Product.ProductID.desc())
    # print(str(o.statement.compile(dialect=postgresql.dialect())))
    # print(o.all())
    return o.all()