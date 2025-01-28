from fastapi import FastAPI, HTTPException
import redis
import redis_lock
import databases
import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Redisクライアント設定
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

# データベース接続設定
DATABASE_URL = "postgresql://username:password@localhost/dbname"
database = databases.Database(DATABASE_URL)

# ロックの有効期限（秒）
LOCK_EXPIRE_TIME = 30  # 30秒間有効


@app.on_event("startup")
async def startup():
    # データベース接続を開始
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    # データベース接続を閉じる
    await database.disconnect()


@app.post("/lock/{row_id}")
async def lock_row(row_id: int):
    """
    行ロックを取得 (Redis + PostgreSQL)
    """
    lock_key = f"lock:row:{row_id}"  # Redisキーとして使用
    lock = redis_lock.Lock(redis_client, lock_key, expire=LOCK_EXPIRE_TIME)

    try:
        # Redisのロックを取得
        if not lock.acquire(blocking=False):
            raise HTTPException(status_code=400, detail=f"Row {row_id} is already locked.")

        # PostgreSQLの行ロックを取得 (悲観的ロック)
        query = select([example_table]).where(example_table.c.id == row_id).for_update()
        async with database.transaction():
            result = await database.fetch_one(query)
            if result is None:
                raise HTTPException(status_code=404, detail=f"Row {row_id} not found.")
        
        return {"message": f"Row {row_id} locked successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unlock/{row_id}")
async def unlock_row(row_id: int):
    """
    行ロックを解除 (Redis + PostgreSQL)
    """
    lock_key = f"lock:row:{row_id}"
    lock = redis_lock.Lock(redis_client, lock_key, expire=LOCK_EXPIRE_TIME)

    try:
        # Redisのロック解除
        if lock.locked():
            lock.release()
            return {"message": f"Row {row_id} unlocked successfully."}
        else:
            raise HTTPException(status_code=400, detail=f"Row {row_id} is not locked.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update/{row_id}")
async def update_row(row_id: int, new_name: str):
    """
    行を更新し、ロックを解除
    """
    lock_key = f"lock:row:{row_id}"
    lock = redis_lock.Lock(redis_client, lock_key, expire=LOCK_EXPIRE_TIME)

    try:
        # Redisのロックを取得
        if not lock.acquire(blocking=False):
            raise HTTPException(status_code=400, detail=f"Row {row_id} is already locked.")

        # PostgreSQLで行の更新
        query = select([example_table]).where(example_table.c.id == row_id).for_update()
        async with database.transaction():
            result = await database.fetch_one(query)
            if result is None:
                raise HTTPException(status_code=404, detail=f"Row {row_id} not found.")
            
            update_query = example_table.update().where(example_table.c.id == row_id).values(name=new_name)
            await database.execute(update_query)

        # ロックを解除
        if lock.locked():
            lock.release()

        return {"message": f"Row {row_id} updated and unlocked successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
