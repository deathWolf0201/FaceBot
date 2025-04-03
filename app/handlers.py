# -*- coding: utf-8 -*-
import os
import time
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from os import listdir
import cv2
import face_recognition
from bot_dp import bot
import app.database.requests as rq
import json


my_photos = "./photos"
router = Router()
file_name = "faces.json"
cache = dict()

@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.last_name is None:
        await rq.set_user(message.from_user.id, message.from_user.first_name)
    else:
        await rq.set_user(message.from_user.id, message.from_user.first_name+" "+message.from_user.last_name)
    await message.answer('Добро пожаловать! Отправьте мне своё фото и вы получите фотографии с вами с мероприятия.')


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Отправьте мне своё фото и вы получите фотографии с вами с мероприятия. Не надо отправлять '
                         'текст, стикер или эмоцию, только фото.')


@router.message(F.photo)
async def send_photos(message: Message):
    global my_photos
    global cache
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    except:
        cache = dict()

    start = time.time()
    if await rq.get_is_processing(message.from_user.id):
        await message.answer('Я уже ищу ваши фотографии. Просьба не отправлять ничего, пока идёт поиск.')
        return
    await message.answer(f'Ищу фотографии. Сейчас в базе {len(listdir(my_photos))} фотографий. Так что надо подождать. Не отправляйте мне сейчас ничего.')
    await rq.set_is_processing(message.from_user.id, True)

    await bot.download(message.photo[-1], f"{message.photo[-1].file_id}.jpg")
    for result in await main_func(f"{message.photo[-1].file_id}.jpg"):
        await message.answer_photo(photo=FSInputFile(result))
        await rq.set_is_any_image(message.from_user.id, True)
    if not await rq.get_is_any_image(message.from_user.id):
        await message.answer('Увы, нет ни одной фотографии. Возможно вы не попали в кадр.')
    else:
        await message.answer('Все фотографии доставлены. Спасибо, что посетили наше мероприятие!')
        await rq.set_is_any_image(message.from_user.id, False)
    os.remove(f"{message.photo[-1].file_id}.jpg")
    await rq.set_is_processing(message.from_user.id, False)
    stop = time.time()
    print(stop-start)



@router.message()
async def response(message: Message):
    await message.answer('Неверный тип сообщения. Отправьте нам фотографию.')


def comparison(image, encoding_face2compare, encoding_face):
    n = len(encoding_face)
    if n % 2 == 0:
        for i in range(n//2):
            res1 = face_recognition.compare_faces(encoding_face2compare,[encoding_face[i]],  0.55)
            res2 = face_recognition.compare_faces(encoding_face2compare,[encoding_face[n-1-i]], 0.55)
            if res1[0] or res2[0]:
                print(f"Success")
                return image
    else:
        for i in range(n//2+1):
            res1 = face_recognition.compare_faces([encoding_face[i]], encoding_face2compare, 0.55)
            res2 = face_recognition.compare_faces([encoding_face[n-1-i]], encoding_face2compare, 0.55)
            if res1[0] or res2[0]:
                print(f"Success")
                return image

    print(f"Failure")


def face_encoding(args):
    start = time.time()
    encoding_face2compare, photo, cache = args[0], args[1], args[2]
    if photo in cache:
        encoding_face = cache[photo]
        print(f"From cache: {photo}")
    else:
        face = face_recognition.load_image_file(photo)
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        encoding_face = face_recognition.face_encodings(face)
        print(f"Not in cache: {photo}")
    print(f"{photo} - processed in {time.time()-start}", end=' ')
    return (photo, encoding_face)


async def main_func(image):
    start = time.time()
    photos = listdir(my_photos)
    face2compare = face_recognition.load_image_file(image)
    face2compare = cv2.cvtColor(face2compare, cv2.COLOR_BGR2RGB)
    encoding_face2compare = face_recognition.face_encodings(face2compare)[0]
    with ProcessPoolExecutor() as process_pool:
        loop = asyncio.get_running_loop()
        args = [(encoding_face2compare, my_photos + '/' + photo, cache) for photo in photos]
        calls = [partial(face_encoding, arg) for arg in args]
        call_coros = []
        for call in calls:
            call_coros.append(loop.run_in_executor(process_pool, call))
        faces = await asyncio.gather(*call_coros)
    pre_results = [comparison(photo, encoding_face2compare, encoding_face) for photo, encoding_face in faces]
    for face in faces:
        if not face[0] in cache:
            cache[face[0]] = [enc.tolist() for enc in face[1]]
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
    results = [result for result in pre_results if result is not None]
    stop = time.time()
    print(f"Время обработки: {stop-start} сек")
    return results
