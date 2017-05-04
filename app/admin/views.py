#coding:utf-8


from datetime import datetime
import json
from flask import request,render_template,flash,redirect,url_for, current_app


from . import admin
from flask_login import login_required,current_user
from .forms import SubMitArticlesForm, ManageArticlesForm,DeleteArticlesForm,DeleteArticleForm,\
    AddArticleTypeForm
from ..modles import Source,ArticleType,Article,Menu,ArticleTypeSetting
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

@admin.route('/edit-articles/<int:id>', methods=['GET', 'POST'])
def editArticles(id):
    article = Article.query.get_or_404(id)
    form =SubMitArticlesForm()
    sources=[(s.id, s.name) for s in Source.query.all()]
    form.source.choices= sources
    types = [(t.id, t.name) for t in ArticleType.query.all()]
    form.types.choices=types

    if form.validate_on_submit():
        articleType = ArticleType.query.get_or_404(int(form.types.data))
        article.articleType = articleType
        source = Source.query.get_or_404(int(form.source.data))
        article.source = source

        article.title = form.title.data
        article.content = form.content.data
        article.summary = form.summary.data
        article.update_time = datetime.utcnow()
        db.session.add(article)
        db.session.commit()
        flash(u'博文更新成功！', 'success')
        return redirect(url_for('main.articleDetails', id=article.id))
    form.source.data = article.source_id
    form.title.data = article.title
    form.content.data = article.content
    form.types.data = article.article_type_id
    form.summary.data = article.summary
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

@admin.route('/manage_articles/delete-article',methods=['GET','POST'])
@login_required
def delete_article():
    types_id = request.args.get('types_id', -1 , type=int)
    source_id = request.args.get('source_id', -1,type=int)
    form = DeleteArticleForm()

    if form.validate_on_submit():
        articleID= int(form.articleId.data)
        article = Article.query.get_or_404(articleID)
        # count = article.comments.count()
        # for comment in article.comments:
        #     db.session.delete(comment)
        db.session.delete(article)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败','danger')
        else:
            flash(u'成功删除博文和0条评论！' , 'success')
    if form.errors:
        flash(u'删除失败', 'danger')

    return  redirect(url_for('admin.manage_articles', types_id=types_id,source_id=source_id,page=request.args.get('page',1,type=int)))

@admin.route('/manage_articles/delete-articles', methods=['GET','POST'])
@login_required
def delete_articles():
    types_id = request.args.get('types_id', -1,type=int)
    source_id = request.args.get('source_id', -1,type=int)
    form = DeleteArticlesForm()

    if form.validate_on_submit():
        articleIds= json.loads(form.articleIds.data)
        print(articleIds,"abc")
        count=0
        for articleId in articleIds:
            article = Article.query.get_or_404(int(articleId))
            # count += article.comments.count()
            # for comment in article.comments:
            #     db.session.delete(comment)
            db.session.delete(article)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                flash(u'删除失败','danger')
            else:
                flash(u'成功删除%s篇博文和%s条评论！' % (len(articleIds), count), 'success')
        if form.errors:
            flash(u'删除失败！', 'danger')
        return redirect(url_for('admin.manage_articles', types_id=types_id, source_id=source_id, page=request.args.get('page',1,type=int)))


@admin.route('/manage_articleTypes', methods=['GET', 'POST'])
@login_required
def manage_articleTypes():
    # form = AddArticleTypeForm(menus=-1)
    menus = Menu.return_menus()
    return_setting_hide = ArticleTypeSetting.return_setting_hide()

    page = request.args.get('page',1,type=int)
    pagination = ArticleType.query.order_by(ArticleType.id.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    articleTypes = pagination.items
    return render_template('admin/manage_articleTypes.html', articleTypes=articleTypes,
                           pagination=pagination, endpoint='.manage_articleTypes',
                            page=page)


@admin.route('/manage-articleTypes/nav' ,methods=['GET','POST'])
@login_required
def manage_articleTypes_nav():
    # form = AddArticleTypeForm()
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (Menu.query.count() - 1) // \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = Menu.query.order_by(Menu.order.asc()).paginate(
            page, per_page=current_app.config['COMMENTS_PER_PAGE'],
            error_out=False)
    menus = pagination.items
    return render_template('admin/manage_articleTypes_nav.html', menus=menus,
                           pagination=pagination, endpoint='.manage_articleTypes_nav',
                           page=page)



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






