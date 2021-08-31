import datetime as dt
from operator import itemgetter

from fastapi import FastAPI, HTTPException, Query
from database import engine, Session, Base, City, User, Picnic, PicnicRegistration
from external_requests import CheckCityExisting, GetWeatherRequest
from models import RegisterUserRequest, UserModel

app = FastAPI()


@app.post('/create-city/', summary='Create City', description='Создание города по его названию')
def create_city(city: str = Query(description="Название города", default=None)):
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


@app.get('/get-cities/', summary='Get Cities')
def cities_list(q: str = Query(description="Название города", default=None)):
    """
    Получение списка городов
    """
    if q:
        cities = Session().query(City).filter(City.name == q)
    else:
        cities = Session().query(City).all()

    return [{'id': city.id, 'name': city.name, 'weather': city.weather} for city in cities]


@app.get('/users-list/', summary='')
def users_list(q: str = Query(description="Возраст пользователя", default=None)):
    """
    Список пользователей
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


@app.post('/register-user/', summary='CreateUser', response_model=UserModel)
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@app.get('/all-picnics/', summary='All Picnics', tags=['picnic'])
def all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
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


@app.post('/picnic-add/', summary='Picnic Add', tags=['picnic'])
def picnic_add(city_id: int, datetime: dt.datetime):
    p = Picnic(city_id=city_id, time=datetime)
    s = Session()
    s.add(p)
    s.commit()

    return {
        'id': p.id,
        'city': Session().query(City).filter(City.id == p.city_id).first().name,
        'time': p.time,
    }


@app.post('/picnic-register/', summary='Picnic Registration', tags=['picnic'])
def register_to_picnic(user_id: int, picnic_id: int):
    """
    Регистрация пользователя на пикник
    (Этот эндпойнт необходимо реализовать в процессе выполнения тестового задания)
    """
    pr = PicnicRegistration(user_id=user_id, picnic_id=picnic_id)
    s = Session()
    s.add(pr)
    s.commit()
    return {
        'id': pr.id,
        "user": Session().query(User).filter(User.id == user_id).first(),
        "picnic": Session().query(Picnic).filter(Picnic.id == picnic_id).first()
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
