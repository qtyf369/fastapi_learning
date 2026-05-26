from sqlalchemy.ext.asyncio.session import AsyncSession


from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import func, DateTime,Integer,String,Float
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,sessionmaker
from datetime import datetime




#1.创建异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/fastapi_learn"
async_engine = create_async_engine(ASYNC_DATABASE_URL, 
echo=True, 
pool_size=10, 
max_overflow=20)

#2.创建模型类
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(),default=func.now(),comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now(),comment="更新时间")
    


class book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,comment="ID")
    bookname: Mapped[str] = mapped_column(String(255),comment="书名")
    author: Mapped[str] = mapped_column(String(255),comment="作者")
    price: Mapped[float] = mapped_column(Float,comment="价格")
    publisher: Mapped[str] = mapped_column(String(255),comment="出版社")

async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    await create_table()
    yield
    # 关闭
    await async_engine.dispose()

# ---------- 4. 创建 FastAPI 应用 ----------
app = FastAPI(lifespan=lifespan)

AsyncSessionLocal = async_sessionmaker[AsyncSession](bind=async_engine, class_=AsyncSession, expire_on_commit=False)



@app.get("/")
def read_root():
    return {"Hello": "World"}

