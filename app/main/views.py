#coding:utf-8
from flask import render_template,request,current_app
from . import main
from ..modles import Article,BlogView
from .form import CommentForm
from .. import db


@main.route('/')
def index():
    BlogView.add_view(db)
    page = request.args.get('page',1,type=int)
    pagination = Article.query.order_by(Article.create_time.desc()).paginate(
        page, per_page=current_app.config['ARTICLES_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('index.html', articles=articles,
                           pagination=pagination, endpoint='.index')

@main.route('/article-detials/<int:id>', methods=['GET','POST'])
def articleDetails(id):
    # BlogView.add_view(db)
    form = CommentForm(request.form, follow=-1)
    article = Article.query.get_or_404(id)
    # return render_template('article_detials.html', User=User, article=article,
    #                        comments=comments, pagination=pagination, page=page,
    #                        form=form, endpoint='.articleDetails', id=article.id)

