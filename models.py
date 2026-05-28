from sqlalchemy import  Integer, String, Float, DateTime, func
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped   # 忘记导入 Mapped
from sqlalchemy import Integer




class Base(DeclarativeBase):  # 基础模型类，所有模型类都继承自这个类
    __abstract__ = True  # 标记为抽象类，不能直接实例化
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class Book(Base):  # 图书模型类，每个模型类对应一个数据库表，每个字段对应一个数据库字段
    __tablename__ = "books"  # 表名
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment="ID")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")