from sqlalchemy import *
from sqlalchemy.orm import *

DATABASE_URL = "sqlite:///app.db"
engine = create_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    """Базовый класс моделей."""

class User(Base):
    __table__ = Table("Users", Base.metadata, autoload_with=engine)


# Создаём фабрику сессий
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _to_dict(user):
    """Преобразует объект User в словарь для GUI."""
    if user is None:
        return None
    return {
        "id": user.id,
        "login": user.login,
        "password": user.password,
        "role": user.role,
        "full_name": user.full_name,
        "locked": bool(user.is_locked),
        "attempts": user.attempts,
    }


def all_users():
    """Возвращает список всех пользователей в виде словарей."""
    with SessionLocal() as session:
        users = session.scalars(select(User).order_by(User.id)).all()
        return [_to_dict(u) for u in users]


def find_user(login, password):
    """Ищет пользователя по логину и паролю. Возвращает словарь или None."""
    with SessionLocal() as session:
        user = session.scalars(
            select(User).where(User.login == login, User.password == password)
        ).first()
        return _to_dict(user)


def user_by_login(login):
    """Возвращает пользователя по логину (словарь) или None."""
    with SessionLocal() as session:
        user = session.scalars(
            select(User).where(User.login == login)
        ).first()
        return _to_dict(user)


def login_exists(login):
    """Проверяет, существует ли пользователь с таким логином."""
    with SessionLocal() as session:
        return session.scalars(
            select(User).where(User.login == login)
        ).first() is not None


def add_user(login, password, role, full_name):
    """Добавляет нового пользователя."""
    with SessionLocal() as session:
        if session.scalars(select(User).where(User.login == login)).first():
            return False  # логин уже занят
        user = User(
            login=login,
            password=password,
            role=role,
            full_name=full_name,
            is_locked=False,
            attempts=0,
        )
        session.add(user)
        session.commit()
        return True


def update_user(login, password, role, full_name):
    """Обновляет данные пользователя по логину."""
    with SessionLocal() as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.password = password
        user.role = role
        user.full_name = full_name
        session.commit()
        return True


def delete_user(login):
    """Удаляет пользователя по логину."""
    with SessionLocal() as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        session.delete(user)
        session.commit()
        return True


def register_fail(login):
    """
    Регистрирует неудачную попытку входа.
    Возвращает True, если пользователь заблокирован (>=3 попыток).
    """
    with SessionLocal() as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.attempts = (user.attempts or 0) + 1
        if user.attempts >= 3:
            user.is_locked = True
            session.commit()
            return True
        session.commit()
        return False


def reset_attempts(login):
    """Сбрасывает счётчик неудачных попыток."""
    with SessionLocal() as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.attempts = 0
        session.commit()
        return True


def unlock_user(login):
    """Разблокирует пользователя и сбрасывает попытки."""
    with SessionLocal() as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.is_locked = False
        user.attempts = 0
        session.commit()
        return True