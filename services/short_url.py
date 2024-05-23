import asyncio
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.short_url import ShortUrl
from typing import List, Optional
from sqlalchemy.orm import load_only
from pydantic import HttpUrl


class ShortUrlService:

    # 取得單一短網址
    @staticmethod
    async def get_short_url(
        async_session: AsyncSession, **kwargs
    ) -> Optional[ShortUrl]:
        query = select(ShortUrl).filter_by(**kwargs)
        result = await async_session.execute(query)
        return result.scalar()

    # 取得短網址列表，如果帶入 page=-1 則獲取全部
    @staticmethod
    async def get_short_url_list(
        async_session: AsyncSession, page: int = 1, limit: int = 20, **kwargs
    ):
        results = []
        batch_size = 10000
        base_query = select(ShortUrl)

        if kwargs:
            # 如果有提供過濾條件，執行過濾條件查詢
            for key, value in kwargs.items():
                # 如果是列表，則執行分批次查詢
                if isinstance(value, list):
                    tasks = []
                    # 分批次處理每個列表參數
                    for i in range(0, len(value), batch_size):
                        batch = value[i : i + batch_size]
                        query = base_query.filter(getattr(ShortUrl, key).in_(batch))
                        if page != -1:
                            query = query.offset((page - 1) * limit).limit(limit)
                        tasks.append(async_session.execute(query))

                    # 異步執行所有批次查詢
                    batch_results = await asyncio.gather(*tasks)
                    for batch_result in batch_results:
                        results.extend(batch_result.scalars().all())
                # 否則直接使用過濾條件查詢
                else:
                    query = base_query.filter(getattr(ShortUrl, key) == value)
                    if page != -1:
                        query = query.offset((page - 1) * limit).limit(limit)
                    result = await async_session.execute(query)
                    results.extend(result.scalars().all())
        else:
            # 如果沒有提供過濾條件，執行基本查詢
            query = base_query
            if page != -1:
                query = query.offset((page - 1) * limit).limit(limit)
            result = await async_session.execute(query)
            results.extend(result.scalars().all())

        return results

    # 新增單一短網址
    @staticmethod
    async def create_short_url(async_session: AsyncSession, **kwargs):
        short_url = ShortUrl(**kwargs)
        async_session.add(short_url)
        await async_session.commit()
        await async_session.refresh(short_url)  # 刷新對象以獲取自動生成的字段
        return short_url

    # 更新短網址
    @staticmethod
    async def update_short_url(async_session: AsyncSession, short_code: str, **kwargs):
        query = (
            update(ShortUrl).where(ShortUrl.short_code == short_code).values(**kwargs)
        )
        await async_session.execute(query)
        await async_session.commit()

        # 確認更新後返回更新的對象
        return await ShortUrlService.get_short_url(async_session, short_code=short_code)

    # 刪除短網址
    @staticmethod
    async def delete_short_url(async_session: AsyncSession, short_code: str):
        query = delete(ShortUrl).where(ShortUrl.short_code == short_code)
        result = await async_session.execute(query)
        await async_session.commit()
        if result.rowcount == 0:
            return None
        return result

    # 批量新增短網址
    @staticmethod
    async def create_batch_short_url(
        async_session: AsyncSession, short_urls: List[ShortUrl], batch_size: int = 1000
    ):
        # 使用 SQLAlchemy 模型的 __dict__ 屬性，並過濾掉 SQLAlchemy 特定的屬性
        short_urls = [
            ShortUrl(
                **{
                    key: value
                    for key, value in short_url.__dict__.items()
                    if not key.startswith("_")
                }
            )
            for short_url in short_urls
        ]
        # 分批次插入資料

        async_session.add_all(short_urls)
        await async_session.commit()
        return short_urls

    # 批量刪除短網址
    @staticmethod
    async def delete_batch_short_url(async_session: AsyncSession, ids: List[int]):
        query = delete(ShortUrl).where(ShortUrl.id.in_(ids))
        result = await async_session.execute(query)
        await async_session.commit()
        return result
