#coding:utf-8

from app import db,login_manager
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

article_types = {u'开发语言': ['Python', 'Java', 'JavaScript'],
                 'Linux': [u'Linux成长之路', u'Linux运维实战', 'CentOS', 'Ubuntu'],
                 u'网络技术': [u'思科网络技术', u'其它'],
                 u'数据库': ['MySQL', 'Redis'],
                 u'爱生活，爱自己': [u'生活那些事', u'学校那些事',u'感情那些事'],
                 u'Web开发': ['Flask', 'Django'],}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    avatar_hash=db.Column(db.String(32))

    @staticmethod
    def insert_admin(email,username,password):
        user = User(email = email,username=username, password=password)
        db.session.add(user)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('passwird us bit a readavke attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    def gravatar(self, size=40, default='identicon', rating='g'):
        url = 'http://gravatar.duoshuo.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

# callback function for flask-login extentsion
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class BlogInfo(db.Model):
    __tablename__ = 'blog_info'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64))
    signature =db.Column(db.Text)
    navbar = db.Column(db.String(64))

    @staticmethod
    def insert_blog_info():
        blog_mini_info = BlogInfo(title=u'开源博客系统Blog_mini',
                                  signature=u'让每个人都轻松拥有可管理的个人博客！— By xpleaf',
                                  navbar='inverse')
        db.session.add(blog_mini_info)
        db.session.commit()
class Menu(db.Model):
    __tablename__ ='menus'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64), unique=True)
    types = db.relationship('ArticleType',backref='menu',lazy='dynamic')
    order = db.Column(db.Integer, default=0, nullable=False)

    def sort_delete(self):
        for menu in Menu.query.order_by(Menu.order).offset(self.order).all():
            menu.order -= 1
            db.session.add(menu)

    @staticmethod
    def insert_menus():
        menus = [u'web开发', u'数据库',u'网络技术',u'爱生活，爱自己',u'linux世界',u'开发语言']
        for name in menus:
            menu =Menu(name=name)
            db.session.add(menu)
            db.session.commit()
            menu.order = menu.id
            db.session.add(menu)
            db.session.commit()

    @staticmethod
    def return_menus():
        menus = [(m.id, m.name) for m in Menu.query.all()]
        menus.append((-1,u'不选择导航（该分类单独成一导航'))
        return menus

    def __repr__(self):
        return '<Menu %r> ' % self.name
class ArticleType(db.Model):
    __tablename__ = 'articleTypes'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    introduction = db.Column(db.Text,default=None)
    articles = db.relationship('Article', backref='articleType',lazy= 'dynamic')
    menu_id = db.Column(db.Integer,db.ForeignKey('menus.id'),default=None)
    setting_id = db.Column(db.Integer,db.ForeignKey('articleTypeSettings.id'))

    @staticmethod
    def insert_system_articleType():
        articleType = ArticleType(name=u'未分类',
                                  introduction=u'系统默认分类，不可删除',
                                  setting=ArticleTypeSetting.query.filter_by(protected=True).first())
        db.session.add(articleType)
        db.session.commit()

    @staticmethod
    def insert_articleTypes():
        articleTypes=['Python', 'Java', 'JavaScript', 'Django',
                        'CentOS', 'Ubuntu', 'MySQL', 'Redis',
                        u'Linux成长之路', u'Linux运维实战', u'其它',
                        u'思科网络技术', u'生活那些事', u'学校那些事',
                        u'感情那些事', 'Flask']

        for name in articleTypes:
            articleType = ArticleType(name=name,setting=ArticleTypeSetting(name=name))
            db.session.add(articleType)
        db.session.commit()

    @property
    def is_protected(self):
        if self.setting:
            return self.setting.protected
        else:
            return False

    @property
    def is_hide(self):
        if self.setting:
            return self.setting.hide
        else:
            return False

    def __repr__(self):
        return '<Type> %r' % self.name

class Article(db.Model):
    __tablename__ ='articles'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Integer, unique=True)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    num_of_view = db.Column(db.Integer, default=0)
    article_type_id = db.Column(db.Integer, db.ForeignKey('articleTypes.id'))
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    comments = db.relationship('Comment', backref='article', lazy='dynamic')
    def __repr__(self):
        return '<Article %r>' % self.title

    @staticmethod
    def add_view(article,db):
        article.num_of_view += 1
        db.session.add(article)
        db.session.commit()




class ArticleTypeSetting(db.Model):
    __tablename__ = 'articleTypeSettings'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    protected = db.Column(db.Boolean,default=False)
    hide = db.Column(db.Boolean,default=False)
    types = db.relationship('ArticleType', backref='setting', lazy='dynamic')

    @staticmethod
    def insert_system_setting():
        system= ArticleTypeSetting(name='system', protected=True,hide=True)
        db.session.add(system)
        db.session.commit()

    @staticmethod
    def insert_default_settings():
        system_setting = ArticleTypeSetting(name='system',protected=True,hide=True)
        common_setting = ArticleTypeSetting(name='common', protected=False,hide=False)
        db.session.add(system_setting)
        db.session.add(common_setting)
        db.session.commit()

    @staticmethod
    def return_setting_hide():
        return [(2, u'公开'), (1, u'隐藏')]

    def __repr__(self):
        return '<ArticleTypeSetting %r>' % self.name

class Source(db.Model):
    __tablename__ ='sources'
    id= db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    articles= db.relationship('Article', backref='source',lazy='dynamic')

    @staticmethod
    def insert_sources():
        sources=(u'原创',
                 u'转载',
                 u'翻译'
                 )
        for s in sources:
            source = Source.query.filter_by(name=s).first()
            if source is None:
                source = Source(name=s)
            db.session.add(source)
        db.session.commit()

    def __repr__(self):
        return '<Source %r>' % self.name




class BlogView(db.Model):
    __tablename__ = 'blog_view'
    id = db.Column(db.Integer, primary_key=True)
    num_of_view = db.Column(db.BigInteger, default=0)

    @staticmethod
    def insert_view():
        view = BlogView(num_of_view=0)
        db.session.add(view)
        db.session.commit()

    @staticmethod
    def add_view(db):
        view = BlogView.query.first()
        view.num_of_view += 1
        db.session.add(view)
        db.session.commit()

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(64))
    avatar_hash= db.Column(db.String(128), default='notReply')
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    disabled = db.Column(db.Boolean, default=False)
    comment_type = db.Column(db.String(64), default='comment')
    reply_to = db.Column(db.String(128), default='notReply')

    def __init__(self):
        super(Comment,self).__init__()
        if self.author_email is not None and self.avatar_hash is None:
            self.avatar_hash=hashlib.md5(self.author_email.encode('utf-8')).hexdigest()



