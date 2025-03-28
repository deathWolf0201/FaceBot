from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select


async def set_user(tg_id, user_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, user_name=user_name, image_id="", is_processing=False, is_any_image=False))
            await session.commit()


async def get_is_any_image(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user.is_any_image


async def set_is_any_image(tg_id, state):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.is_any_image = state
        session.add(user)
        await session.commit()


async def get_image(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user.image_id


async def set_image_id(tg_id, image_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.image_id = image_id
        session.add(user)
        await session.commit()


async def get_is_processing(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user.is_processing


async def set_is_processing(tg_id, state):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user.is_processing = state
        session.add(user)
        await session.commit()


