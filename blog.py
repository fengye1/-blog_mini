#coding:utf-8
from app import app
from app.modles import BlogInfo, ArticleType, Menu, article_types,ArticleTypeSetting,User,\
    Source,Article,BlogView

app.jinja_env.globals['BlogInfo'] = BlogInfo
app.jinja_env.globals['article_types'] = article_types
app.jinja_env.globals['Menu'] = Menu
app.jinja_env.globals['ArticleType'] = ArticleType
app.jinja_env.globals['Source'] = Source
app.jinja_env.globals['Article'] = Article
app.jinja_env.globals['BlogView']= BlogView



def init_data():
    BlogInfo.insert_blog_info()
    ArticleTypeSetting.insert_system_setting()
    ArticleType.insert_system_articleType()
    Menu.insert_menus()
    ArticleType.insert_articleTypes()
    User.insert_admin(email='blog_mini@163.com', username='blog_mini', password='blog_mini')
    Source.insert_sources()
    BlogView.insert_view()

if __name__ == '__main__':

    # init_data()
    # app.run(debug=True)
    app.run()