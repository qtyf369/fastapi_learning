from sqlalchemy.ext.asyncio.session import AsyncSession


from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import func, DateTime,Integer,String,Float
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,async_sessionmaker
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


# ---------- 5. 创建异步会话工厂 ----------
AsyncSessionLocal = async_sessionmaker[AsyncSession](bind=async_engine, class_=AsyncSession, expire_on_commit=False) # 异步会话工厂，用于创建异步会话，每个请求创建一个会话，会话在请求处理完成后自动关闭

#依赖项，用于在路由处理函数中注入异步会话
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:# 异步会话工厂创建异步会话,会话加小括号就是生成一个异步会话对象。
        try:
            yield session
        finally:
            await session.close()





@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__": # 主程序入口，用于启动服务器
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
   