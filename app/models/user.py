from sqlalchemy import Column, Integer, String

from app.models import Base, row_to_dict, session_scope


class User(Base):
    __tablename__ = 'user'

    user_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True
    )
    email = Column(String(length=512), nullable=False, unique=True)
    username = Column(String(length=64), nullable=True)
    password = Column(String(length=64), nullable=False)
    description = Column(String(length=512), nullable=True)
    thumbnail = Column(String(length=64), nullable=False)

    @classmethod
    def get(cls, user_id):
        '''user_idに紐づく必要最低限のuser情報を取得
        Args:
            user_id:    ユーザID
        Returns:
            username:      ニックネーム
            description:        プロファイル
            thumbnail:   ツイッターネーム
        '''
        with session_scope() as session:
            rows = session.query(
                cls.username,
                cls.description,
                cls.thumbnail
            ).filter(
                cls.user_id == user_id
            ).first()

            if not rows:
                return None

            return rows._asdict()

    @classmethod
    def get_by_email(cls, email):
        '''emailに紐づく必要最低限のuser情報を取得
        Args:
            email:    学番メール
        Returns:
            username:      ニックネーム
            description:        プロファイル
            thumbnail:   ツイッターネーム
        '''
        with session_scope() as session:
            rows = session.query(
                cls.username,
                cls.description,
                cls.thumbnail
            ).filter(
                cls.email == email
            ).first()

            if not rows:
                return None

            return rows._asdict()

    @classmethod
    def get_email(cls, user_id):
        '''user_idに紐づくemail取得
        Args:
            user_id:    ユーザID
        Returns:
            email:      学番メール
        '''
        with session_scope() as session:
            rows = session.query(
                cls.email,
            ).filter(
                cls.user_id == user_id
            ).first()

            if not rows:
                return None

            return rows._asdict()

    @classmethod
    def get_user_all(cls, user_id):
        '''user_idに紐づくuser情報(password以外)の取得
        '''
        with session_scope() as session:
            rows = session.query(
                cls.user_id,
                cls.email,
                cls.username,
                cls.description,
                cls.thumbnail
            ).filter(
                cls.user_id == user_id
            ).first()

            if not rows:
                return None

            return rows._asdict()

    @classmethod
    def get_users_all(cls):
        '''すべてのuser取得
        '''
        with session_scope() as session:
            rows = session.query(
                cls.user_id,
                cls.email,
                cls.username,
                cls.description,
                cls.thumbnail
            ).all()

            result = [row._asdict() for row in rows]

            return result

    @classmethod
    def get_user_secret(cls, user_id):
        '''user_idに紐づくuser情報(すべて)取得
        '''
        with session_scope() as session:
            row = session.query(cls).filter(cls.user_id == user_id).first()

            return row_to_dict(row)

    @classmethod
    def login(cls, email, password):
        '''emailとpasswordが一致するuser情報を取得
        Args:
            email:      学番メール
            password:   パスワード
        Returns:
            dict: user情報
        '''
        with session_scope() as session:
            rows = session.query(
                cls.user_id,
                cls.email,
                cls.username,
                cls.description,
                cls.thumbnail
            ).filter(
                cls.email == email,
                cls.password == password
            ).order_by(
                cls.user_id.desc()
            ).first()

            if not rows:
                return None

            return rows._asdict()

    @classmethod
    def is_exist_by_email(cls, email):
        '''同じ学番メールのユーザが存在するかどうかをboolで返却
        Args:
            email:  学番メール
        Returns:
            bool:
        '''
        with session_scope() as session:
            count = session.query(
                cls
            ).filter(
                cls.email == email
            ).count()

            if count > 0:
                return True
            else:
                return False

    @classmethod
    def is_exist_by_username(cls, username):
        '''同じニックネームのユーザが存在するかどうかをboolで返却
        Args:
            nike_name:  ニックネーム
        Returns:
            bool:
        '''
        with session_scope() as session:
            count = session.query(
                cls
            ).filter(
                cls.username == username
            ).count()

            if count > 0:
                return True
            else:
                return False

    @classmethod
    def post(cls, params):
        '''user登録
        Args:
            params:
                * email:        学番メール
                * password:     パスワード
                * username:    ニックネーム
                description:        プロファイル
                thumbnail:   ツイッターネーム

        * 必須
        '''
        cls._check_length(params)

        with session_scope() as session:
            data = cls(
                **params
            )
            session.add(data)

    @classmethod
    def put(cls, user_id, params):
        '''userの基本情報(password以外)を更新
        '''
        cls._check_length(params)

        with session_scope() as session:
            data = cls(
                user_id=user_id,
                **params
            )

            # mergeして1回commit
            session.merge(data)
            session.commit()

    @classmethod
    def put_password(cls, user_id, password, new_password):
        '''userのpassword更新
        '''
        with session_scope() as session:
            user = cls.get_user_secret(user_id)

            if user.get('password') != password:
                raise Exception('invalid password')

            data = cls(
                user_id=user_id,
                password=new_password
            )

            # mergeして1回commit
            session.merge(data)
            session.commit()

    @classmethod
    def _check_length(cls, params):
        # length_check
        username = params.get('username')
        if username:
            if len(username) > 20:
                raise Exception('over length')

        email = params.get('email')
        if email:
            if len(email) > 50:
                raise Exception('over length')

        description = params.get('description')
        if description:
            if len(description) > 200:
                raise Exception('over length')

        thumbnail = params.get('thumbnail')
        if thumbnail:
            if len(thumbnail) > 15:
                raise Exception('over length')

        return
