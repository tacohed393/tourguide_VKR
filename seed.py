import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.models.place import Place
from app.services.ml_service import get_embedding


TEST_PLACES = [
    # --- МОСКВА ---
    {
        "name": "Красная Площадь",
        "city": "Moscow",
        "type": "Landmark",
        "description": "Сердце России, исторический центр Москвы с видом на Кремль и Собор Василия Блаженного.",
        "search_context": "Красная Площадь. Главная достопримечательность, история, прогулки, брусчатка, мавзолей Ленина, ГУМ, мороженое, сувениры, зима, каток, ярмарка, центр города. Рядом рестораны и кафе."
    },
    {
        "name": "Парк Горького",
        "city": "Moscow",
        "type": "Park",
        "description": "Главный парк столицы. Идеальное место для отдыха, спорта и пикников на набережной.",
        "search_context": "Парк Горького. Природа, деревья, набережная Москвы-реки, велосипеды, самокаты, прогулка с детьми, свидание, лето, отдых, пикник, катамараны. Есть еда, бургеры, кофе, уличная еда."
    },
    {
        "name": "Депо.Москва",
        "city": "Moscow",
        "type": "Food",
        "description": "Крупнейший фудмолл в Европе. Гастрономический квартал в здании бывшего трамвайного депо.",
        "search_context": "Депо.Москва. Еда, рестораны, гастромаркет, фастфуд, высокая кухня, бар, коктейли, тусовка, завтрак, обед, ужин, встречи с друзьями, шумное место, много людей, вкусно поесть."
    },

    # --- САНКТ-ПЕТЕРБУРГ ---
    {
        "name": "Эрмитаж",
        "city": "Saint Petersburg",
        "type": "Museum",
        "description": "Один из величайших музеев мира в Зимнем дворце. Миллионы экспонатов искусства.",
        "search_context": "Эрмитаж. Искусство, картины, история, цари, дворец, культура, дождь (спрятаться от погоды), экскурсия, долго ходить, интересно, образование. Внутри есть кафе."
    },
    {
        "name": "Севкабель Порт",
        "city": "Saint Petersburg",
        "type": "Public Space",
        "description": "Модное пространство у моря на Васильевском острове. Вид на залив, выставки и бары.",
        "search_context": "Севкабель Порт. Море, Финский залив, закат, романтика, современное искусство, выставки, концерты, вечеринки, каток зимой, бары, стритфуд, молодежное место, хипстеры."
    },
    {
        "name": "Улица Рубинштейна",
        "city": "Saint Petersburg",
        "type": "Nightlife",
        "description": "Главная ресторанная улица города. Барная линия с десятками заведений на любой вкус.",
        "search_context": "Улица Рубинштейна. Бары, алкоголь, вечеринка, ночь, рестораны, вкусная еда, знакомства, тусовка, прогулка, выпить, коктейли, музыка, центр."
    },

    # --- ОМСК ---
    {
        "name": "Skuratov Coffee (Флагман)",
        "city": "Omsk",
        "type": "Cafe",
        "description": "Родина знаменитых брю-баров. Стильный интерьер, отличный кофе и атмосфера для работы.",
        "search_context": "Skuratov Coffee (Флагман). Кофе, кофейня, завтрак, работа с ноутбуком, фриланс, спокойное место, вкусный десерт, круассаны, эйр латте, колд брю, встреча, уют."
    },
    {
        "name": "Омская Крепость",
        "city": "Omsk",
        "type": "Landmark",
        "description": "Исторический комплекс на берегу Иртыша. Восстановленные ворота и здания 18-19 веков.",
        "search_context": "Омская Крепость. История, достопримечательность, Иртыш, река, набережная, прогулки, экскурсии, Тобольские ворота, памятник, культура, центр города, фотосессия."
    },
    {
        "name": "Птичья Гавань",
        "city": "Omsk",
        "type": "Nature",
        "description": "Природный парк в черте города. Озера, перелетные птицы и тишина.",
        "search_context": "Птичья Гавань. Природа, экология, парк, птицы, животные, тишина, спокойствие, прогулка с детьми, свежий воздух, озеро, осень, лето, наблюдение."
    }
]

async def seed_data():
    
    
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as db:
        await db.execute(text("TRUNCATE TABLE places RESTART IDENTITY"))
        for data in TEST_PLACES:
            print(f"Обрабатываю: {data['name']}...")
            
            
            # vector = get_embedding(data["description"])
            text_for_vector = data.get("search_context", data["description"])
            vector = await get_embedding(text_for_vector)
            
            place = Place(
                name=data["name"],
                city=data["city"],
                type=data["type"],
                description=data["description"],
                search_context=text_for_vector,
                embedding=vector
            )
            db.add(place)
        
        await db.commit()
        print("Данные загружены")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_data())