#coding:utf-8


from datetime import datetime
import json
from flask import request,render_template,flash,redirect,url_for


from . import admin
from flask_login import login_required,current_user
from .forms import SubMitArticlesForm
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


@admin.route('/manage_articles')
def manage_articles():

    return render_template('admin/admin_base.html')


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






