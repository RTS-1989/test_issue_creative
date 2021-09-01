import datetime as dt
from operator import itemgetter

from fastapi import FastAPI, HTTPException, Query
from database import Session, City, User, Picnic, PicnicRegistration
from external_requests import CheckCityExisting
from models import RegisterUserRequest, UserModel, CityModel, PicnicModel, PicnicRegistrationModel

app = FastAPI()


@app.post('/cities/', summary='Create City', response_model=CityModel, tags=["cities"])
def create_city(city: str = Query(description="Название города", default=None)):
    """Создание города:

    - **id**: Идентификатор города в базе данных
    - **name**: Имя города
    - **weather**: Прогноз погоды
    """
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    check = CheckCityExisting()
    if not check.check_existing(city):
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = Session().query(City).filter(City.name == city.capitalize()).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        s = Session()
        s.add(city_object)
        s.commit()

    return {'id': city_object.id, 'name': city_object.name, 'weather': city_object.weather}


@app.get('/cities/', summary='Get Cities', tags=["cities"])
def get_cities_list(q: str = Query(description="Название города", default=None)):
    """
    Получение списка городов:

    - **id**: Идентификатор города в базе данных
    - **name**: Имя города
    - **weather**: Прогноз погоды
    """
    if q:
        cities = Session().query(City).filter(City.name == q)
    else:
        cities = Session().query(City).all()

    return [{'id': city.id, 'name': city.name, 'weather': city.weather} for city in cities]


@app.get('/users/', summary='Get users list', tags=["users"])
def get_users_list(q: str = Query(description="Возраст пользователя", default=None)):
    """
    Список пользователейЖ

    - **id**: Идентификатор пользователя в базе данных
    - **name**: Имя пользователя
    - **surname**: Фамилия пользователя
    - **age**: Возраст пользователя
    """
    users = Session().query(User).all()
    base_users_list = [{
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'age': user.age,
    } for user in users]
    if q in ["asc", "desc"]:
        order = q == "desc"
        return sorted(base_users_list, key=itemgetter("age"), reverse=order)
    else:
        return base_users_list


@app.post('/users/', summary='Create User', response_model=UserModel, tags=["users"])
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя:

    - **id**: Идентификатор пользователя в базе данных
    - **name**: Имя пользователя
    - **surname**: Фамилия пользователя
    - **age**: Возраст пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@app.get('/picnics/', summary='All Picnics', tags=['picnic'])
def get_all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                    past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
    - **id**: Идентификатор пикника в базе данных
    - **city**: Город, в котором будет проводится пикник
    - **time**: Время проведения пикника
    - **users**: Пользователи, зарегистрировавшиеся на пикник
    """
    picnics = Session().query(Picnic)
    if datetime is not None:
        picnics = picnics.filter(Picnic.time == datetime)
    if not past:
        picnics = picnics.filter(Picnic.time >= dt.datetime.now())

    return [{
        'id': pic.id,
        'city': Session().query(City).filter(City.id == pic.id).first().name,
        'time': pic.time,
        'users': [
            {
                'id': pr.user.id,
                'name': pr.user.name,
                'surname': pr.user.surname,
                'age': pr.user.age,
            }
            for pr in Session().query(PicnicRegistration).filter(PicnicRegistration.picnic_id == pic.id)],
    } for pic in picnics]


@app.post('/picnics/', summary='Add Picnic', tags=['picnic'], response_model=PicnicModel)
def add_picnic(city_id: int, datetime: dt.datetime):
    """
    Добавление пикника:

    - **id**: Идентификатор пикника в базе данных
    - **city**: Город, в котором будет проводится пикник
    - **time**: Время проведения пикника
    """
    p = Picnic(city_id=city_id, time=datetime)
    s = Session()
    s.add(p)
    s.commit()

    return {
        'id': p.id,
        'city': Session().query(City).filter(City.id == p.city_id).first().name,
        'time': p.time,
    }


@app.post('/user-registration/', summary='Picnic Registration',
          tags=['picnic'], response_model=PicnicRegistrationModel)
def register_to_picnic(user_id: int, picnic_id: int):
    """
    Регистрация пользователя на пикник
    (Этот эндпойнт необходимо реализовать в процессе выполнения тестового задания)

    - **id**: Идентификатор регистрации на пикник
    - **user_surname**: Фамилия пользователя, регистрирующегося на пикник
    - **picnic_id**: Идентификатор пикника
    """
    pr = PicnicRegistration(user_id=user_id, picnic_id=picnic_id)
    s = Session()
    s.add(pr)
    s.commit()
    return {
        'id': pr.id,
        "user_surname": Session().query(User).filter(User.id == user_id).first().surname,
        "picnic_id": Session().query(Picnic).filter(Picnic.id == picnic_id).first().city_id
    }

# Минимиальный уровень Задача 4
# 1) На данном этапе приложение имеет БД файлового типа (текстовый файл).
# При увеличении количества запросов могут возникнуть проблемы при записи и чтении
# данных от множества пользователей. Использование СУБД, скажем PostgresQL
# решило бы эту проблему, так как в данном случае обработка множественных
# обращений к данным реализована и при параллельном обращении включаются блокировки,
# чтобы разграничить доступ к данным.
# 2) При множестве запросов некоторые запросы могут дублироваться. В данном случае можно
# было бы задуматься о кешировании данных.
# 3) Также в данном случае база данных и приложение находятся в одном месте. В случае
# увеличения нагрузки надо вынести на отдельный сервер. Также это позволит масштабировать
# отдельно приложение и базу данных.
# 4) Необходимо организовать очередь запросов.
# 5) Ведение логов. В случае увеличения запросов нужно будет отслеживать нарастающий объем ошибок.
