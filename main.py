from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import DateTime, Float, Integer, String, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.responses import PlainTextResponse


# 1.创建异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/fastapi_learn"
async_engine = create_async_engine(ASYNC_DATABASE_URL,
                                   echo=True,
                                   pool_size=10,
                                   max_overflow=20)

# 2.创建模型类
from models import Base, Book 







async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("数据库表创建完成")


@asynccontextmanager  # 异步上下文管理器，用于在 FastAPI 应用启动和关闭时执行一些操作
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    await create_table()
    yield
    # 关闭时关闭数据库引擎
    await async_engine.dispose()

# ---------- 4. 创建 FastAPI 应用 ----------
app = FastAPI(lifespan=lifespan)


# ---------- 5. 创建异步会话工厂 ----------
AsyncSessionLocal = async_sessionmaker[AsyncSession](
    # 异步会话工厂，用于创建异步会话，每个请求创建一个会话，会话在请求处理完成后自动关闭
    bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# 依赖项，用于在路由处理函数中注入异步会话


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:  # 异步会话工厂创建异步会话,会话加小括号就是生成一个异步会话对象。
        try:
            yield session
        finally:
            await session.close()


@app.get("/books")
async def read_books(db: AsyncSession = Depends(get_db)):
    async with db.begin():  # 这里不能用as conn，因为db.begin()已经返回了一个连接对象，with as会返回一个asynsessiontransaction对象
        books = await db.execute(select(Book))  # 这里Book是模型类，在类里定义了表名和字段
        return {"books": books.scalars().all()}


@app.get("/", response_class=PlainTextResponse)
async def read_root():
    return "宝宝，我爱你。"

#筛选接口
@app.get("/books/easy")
async def read_books_easy(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        books = await db.execute(select(Book).where(Book.price <= 100))
        return {"books": books.scalars().all()} # 这里books.scalars().all()返回的是一个列表，每个元素都是一个Book对象，会被FastAPI自动转换为JSON格式，形成一个字典



@app.get("/books/{id}")
async def read_book(id: int, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Book).where(Book.id == id))
        return {"book": result.scalar_one_or_none()}







if __name__ == "__main__":  # 主程序入口，用于启动服务器
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
