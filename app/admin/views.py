#coding:utf-8


from datetime import datetime
import json
from flask import request,render_template,flash,redirect,url_for, current_app


from . import admin
from flask_login import login_required,current_user
from .forms import SubMitArticlesForm, ManageArticlesForm,DeleteArticlesForm,DeleteArticleForm
from ..modles import Source,ArticleType,Article
from .. import db


@admin.route('/sumbit-articles', methods=['GET','POST'])
@login_required
def submitArticles():
    form = SubMitArticlesForm()
    sources = [(s.id, s.name) for s in Source.query.all()]
    form.source.choices= sources
    types = [(t.id, t.name) for t in ArticleType.query.all()]
    form.types.choices = types

    if form.validate_on_submit():
        title = form.title.data
        source_id = form.source.data
        content = form.content.data
        type_id = form.types.data
        summary = form.summary.data

        source = Source.query.get(source_id)
        articleType = ArticleType.query.get(type_id)
        if source and ArticleType:
            article = Article(title=title, content= content, summary=summary,
                              source=source, articleType=articleType)
            db.session.add(article)
            db.session.commit()
            flash(u'发表博文成功！', 'success')
            article_id = Article.query.filter_by(title=title).first().id
            return redirect(url_for('main.index'))
    if form.errors:
            flash(u'发表博文失败', 'danger')

    return render_template('admin/submit_articles.html', form=form)


@admin.route('/manage_articles', methods=['GET','POST'])
@login_required
def manage_articles():
    types_id = request.args.get('types_id', -1 , type=int)
    source_id =request.args.get('source_id', -1, type=int)
    form = ManageArticlesForm(request.form, types=types_id,source=source_id)
    form2= DeleteArticleForm()
    form3 = DeleteArticlesForm()  # for delete articles

    types=[(t.id,t.name) for t in ArticleType.query.all()]
    types.append((-1,u'全部分类'))
    form.types.choices = types
    sources = [(s.id, s.name) for s in Source.query.all()]
    sources.append((-1, u'全部来源'))
    form.source.choices = sources

    pagination_search = 0

    if form.validate_on_submit() or\
        (request.args.get('types_id') is not None and request.args.get('source_id') is not None):
        if form.validate_on_submit():
            types_id = form.types.data
            source_id = form.source.data
            page=1
        else:
            types_id=request.args.get('types_id', type=int)
            source_id = request.args.get('source_id', type=int)
            form.types.data = types_id
            form.source.data = source_id
            page = request.args.get('page', 1, type=int)

        result = Article.query.order_by(Article.create_time.desc())
        if types_id != -1:
            articleType = ArticleType.query.get_or_404(types_id)
            result = result.filter_by(articleType=articleType)

        if source_id != -1:
            source = Source.query.get_or_404(source_id)
            result = result.filter_by(source=source)

        pagination_search = result.paginate(
            page, per_page=current_app.config['ARTICLES_PER_PAGE'], error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        articles = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Article.query.order_by(Article.create_time.desc()).paginate(
                page, per_page=current_app.config['ARTICLES_PER_PAGE'],
                error_out=False)
        articles = pagination.items

    return render_template('admin/manage_articles.html', pagination=pagination,
                           endpoint='admin.manage_articles', form=form,form2=form2,form3=form3, types_id=types_id, source_id=source_id,articles=articles)


@admin.route('/manage_articleTypes')
def manage_articleTypes():
    pass


@admin.route('/manage_comments')
def manage_comments():
    pass



@admin.route('/custom_blog_info')
def custom_blog_info():
    return render_template('base.html')


@admin.route('/custom_blog_plugin')
def custom_blog_plugin():
    return render_template('base.html')


@admin.route('/add_plugin')
def add_plugin():
    return render_template('base.html')


@admin.route('/account')
def account():
    return render_template('base.html')


@admin.route('/help')
def help():
    return render_template('base.html')






