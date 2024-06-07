import asyncio
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.access_log import AccessLog
from typing import List, Optional


class AccessLogService:

    # 取得單一訪問紀錄
    @staticmethod
    async def get_access_log(
        async_session: AsyncSession, **kwargs
    ) -> Optional[AccessLog]:
        query = select(AccessLog).filter_by(**kwargs)
        result = await async_session.execute(query)
        return result.scalar()

    # 取得訪問紀錄列表，如果帶入 page=-1 則獲取全部
    @staticmethod
    async def get_access_log_list(
        async_session: AsyncSession, page: int = 1, limit: int = 20, **kwargs
    ) -> dict:
        results = []
        total = 0
        batch_size = 10000
        base_query = select(AccessLog).order_by(AccessLog.accessed_at.desc())

        if kwargs:
            # 如果有提供過濾條件，執行過濾條件查詢
            for key, value in kwargs.items():
                # 如果是列表，則執行分批次查詢
                if isinstance(value, list):
                    tasks = []
                    count_tasks = []
                    # 分批次處理每個列表參數
                    for i in range(0, len(value), batch_size):
                        batch = value[i : i + batch_size]
                        query = base_query.filter(getattr(AccessLog, key).in_(batch))
                        count_query = select(func.count()).select_from(query)
                        if page != -1:
                            query = query.offset((page - 1) * limit).limit(limit)
                        tasks.append(async_session.execute(query))
                        count_tasks.append(async_session.execute(count_query))

                    # 異步執行所有批次查詢
                    batch_results = await asyncio.gather(*tasks)
                    count_results = await asyncio.gather(*count_tasks)
                    for batch_result in batch_results:
                        results.extend(batch_result.scalars().all())
                    for count_result in count_results:
                        total += count_result.scalar()
                # 否則直接使用過濾條件查詢
                else:
                    query = base_query.filter(getattr(AccessLog, key) == value)
                    count_query = select(func.count()).select_from(query)
                    if page != -1:
                        query = query.offset((page - 1) * limit).limit(limit)
                    result = await async_session.execute(query)
                    total_result = await async_session.execute(count_query)
                    results.extend(result.scalars().all())
                    total += total_result.scalar()
        else:
            # 如果沒有提供過濾條件，執行基本查詢
            query = base_query
            count_query = select(func.count()).select_from(base_query)
            if page != -1:
                query = query.offset((page - 1) * limit).limit(limit)
            result = await async_session.execute(query)
            total_result = await async_session.execute(count_query)
            results.extend(result.scalars().all())
            total += total_result.scalar()

        return {"list": results, "total": total}

    # 新增單一訪問紀錄
    @staticmethod
    async def create_access_log(async_session: AsyncSession, **kwargs):
        access_log = AccessLog(**kwargs)
        async_session.add(access_log)
        await async_session.commit()
        await async_session.refresh(access_log)  # 刷新對象以獲取自動生成的字段
        return access_log

    # 刪除訪問紀錄
    @staticmethod
    async def delete_access_log(async_session: AsyncSession, short_code: str):
        query = delete(AccessLog).where(AccessLog.short_code == short_code)
        result = await async_session.execute(query)
        await async_session.commit()
        if result.rowcount == 0:
            return None
        return result

    # 取得不重複的短網址點擊數
    @staticmethod
    async def get_distinct_click_count(async_session: AsyncSession, **kwargs) -> int:
        subquery = (
            select(AccessLog.short_code, AccessLog.ip_address)
            .filter_by(**kwargs)
            .distinct()
            .subquery()
        )
        query = select(func.count()).select_from(subquery)
        result = await async_session.execute(query)
        return result.scalar()
