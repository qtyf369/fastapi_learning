import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, func
from models import Book
# 1.创建异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/fastapi_learn"
async_engine = create_async_engine(ASYNC_DATABASE_URL,
                                   echo=True,
                                   pool_size=10,
                                   max_overflow=20)

books=[Book(bookname=f"枫娇赚到第{i}个200万", author="阿枫", price=99.99, publisher="Python出版社") for i in range(1,50)] # 生成50个book对象，而且都写入内存中，但还没提交到数据库中
# 2.创建异步会话
# ---------- 创建异步会话工厂 ----------
AsyncSessionLocal = async_sessionmaker[AsyncSession](
    # 异步会话工厂，用于创建异步会话，每个请求创建一个会话，会话在请求处理完成后自动关闭
    bind=async_engine, class_=AsyncSession, expire_on_commit=False) #异步会话工厂是统一定制的，后续只要加个小括号就可以创建异步会话。

async def add_books():
    async with AsyncSessionLocal() as session:
        session.add_all(books)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(add_books())