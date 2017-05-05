#coding:utf-8


from datetime import datetime
import json
from flask import request,render_template,flash,redirect,url_for, current_app,jsonify


from . import admin
from flask_login import login_required,current_user
from .forms import SubMitArticlesForm, ManageArticlesForm,DeleteArticlesForm,DeleteArticleForm,\
    AddArticleTypeForm, EditArticleTypeForm, EditArticleNavTypeForm, AddArticleTypeNavForm
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
    form = AddArticleTypeForm(menus=-1)
    form2 = EditArticleTypeForm()

    menus = Menu.return_menus()
    return_setting_hide = ArticleTypeSetting.return_setting_hide()
    form.menus.choices=menus
    form.setting_hide.choices=return_setting_hide
    form2.menus.choices =menus
    form2.setting_hide.choices=return_setting_hide

    page = request.args.get('page',1,type=int)

    if form.validate_on_submit():
        name =form.name.data
        articleType = ArticleType.query.filter_by(name=name).first()
        if articleType:
            flash(u'添加分类失败！该分类名称已经存在.', 'danger')

        else:
            introduction = form.introduction.data
            setting_hide= form.setting_hide.data
            menu = Menu.query.get(form.menus.data)
            if not menu:
                menu = None
            articleType = ArticleType(name=name, introduction=introduction, menu=menu,
                                      setting = ArticleTypeSetting(name=name))

            if setting_hide == 1:
                articleType.setting.hide=True
            if setting_hide ==2:
                articleType.setting.hide=False

            db.session.add(articleType)
            db.session.commit()
            flash(u'添加成功','success')
            return redirect(url_for('.manage_articleTypes'))
    if form.errors:
        flash(u'添加分类失败！请查看填写有无错误。', 'danger')
        return redirect(url_for('.manage_articleTypes'))

    pagination = ArticleType.query.order_by(ArticleType.id.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)

    articleTypes = pagination.items
    return render_template('admin/manage_articleTypes.html', articleTypes=articleTypes,
                           pagination=pagination, endpoint='.manage_articleTypes',
                            page=page,form=form,form2=form2)


# 博文分类
@admin.route('/manage-articleTypes/nav' ,methods=['GET','POST'])
@login_required
def manage_articleTypes_nav():
    form = AddArticleTypeNavForm()
    form2= EditArticleNavTypeForm()
    page = request.args.get('page', 1, type=int)

    if form.validate_on_submit():
        name = form.name.data
        menu = Menu.query.filter_by(name=name).first()
        if menu:
            page=page
            flash(u'添加导航失败！该导航名称已经存在。','danger')
        else:
            menu_count = Menu.query.count()
            menu = Menu(name=name,order=menu_count+1)
            db.session.add(menu)
            db.session.commit()
            flash(u'添加导航成功','success')
        return  redirect(url_for('admin.manage_articleTypes_nav', page=page))
    if page == -1:
        page = (Menu.query.count() - 1) // \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = Menu.query.order_by(Menu.order.asc()).paginate(
            page, per_page=current_app.config['COMMENTS_PER_PAGE'],
            error_out=False)

    menus = pagination.items
    return render_template('admin/manage_articleTypes_nav.html', menus=menus,
                           pagination=pagination, endpoint='.manage_articleTypes_nav',
                           page=page,form=form,form2=form2)



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

@admin.route('/manage-articleTypes/get-articleType-info/<int:id>')
@login_required
def get_articleType_info(id):
    if request.is_xhr:
        articletype = ArticleType.query.get_or_404(id)
        if articletype.is_hide:
            setting_hide =1
        else:
            setting_hide=2
        return jsonify({
            'name':articletype.name,
            'setting_hide':setting_hide,
            'introduction': articletype.introduction,
            'menu':articletype.menu_id or -1
        })

@admin.route('/manage-articletypes/edit-articleType', methods=['POST'])
def edit_articleType():
    form2 = EditArticleTypeForm()
    menus = Menu.return_menus()
    setting_hide=ArticleTypeSetting.return_setting_hide()
    form2.menus.choices=menus
    form2.setting_hide.choices = setting_hide
    page = request.args.get('page',1,type=int)
    if form2.validate_on_submit():
        name = form2.name.data
        articleType_id = int(form2.articleType_id.data)
        articleType = ArticleType.query.get_or_404(articleType_id)
        setting_hide = form2.setting_hide.data

        if articleType.is_protected:
            if form2.name.data != articleType.name or \
                            form2.introduction.data != articleType.introduction:
                flash(u'您只能修改系统默认分类的属性和所属导航！', 'danger')
            else:
                menu = Menu.query.get(form2.menus.data)
                if not menu:
                    menu = None
                articleType.menu = menu
                if setting_hide == 1:
                    articleType.setting.hide = True
                if setting_hide == 2:
                    articleType.setting.hide = False
                db.session.add(articleType)
                db.session.commit()
                flash(u'修改系统默认分类成功！', 'success')
        elif ArticleType.query.filter_by(name=form2.name.data).first() \
            and ArticleType.query.filter_by(name=form2.name.data).first().id != articleType_id:
                flash(u'修改分类失败！该分类名称已经存在。', 'danger')
        else:
            introduction = form2.introduction.data
            menu = Menu.query.get(form2.menus.data)
            if not menu:
               menu = None
            articleType = ArticleType.query.get_or_404(articleType_id)
            articleType.name = name
            articleType.introduction = introduction
            articleType.menu = menu
            if not articleType.setting:
                articleType.setting = ArticleTypeSetting(name=articleType.name)
            if setting_hide == 1:
                    articleType.setting.hide = True
            if setting_hide == 2:
                articleType.setting.hide = False

            db.session.add(articleType)
            db.session.commit()
            flash(u'修改分类成功！', 'success')
        return redirect(url_for('.manage_articleTypes', page=page))
    if form2.errors:
        flash(u'修改分类失败！请查看填写有无错误。', 'danger')
        return redirect(url_for('.manage_articleTypes', page=page))

@admin.route('/mange-articleTypes/delete-articleType/<int:id>')
@login_required
def delete_articleType(id):
    page = request.args.get('page',1,type=int)

    articleType = ArticleType.query.get_or_404(id)
    if articleType.is_protected:
        flash(u'警告：您没有删除系统默认分类的权限！','danger')
        return  redirect(url_for('admin.manage_articleTypes',page=page))
    count=0
    systemType = ArticleTypeSetting.query.filter_by(protected=True).first().types.first()
    articleTypeSetting = ArticleTypeSetting.query.get(articleType.setting_id)
    for article in articleType.articles.all():
        count +=1
        article.articleType_id = systemType.id
        db.session.add(article)
        db.session.commit()
    if articleTypeSetting:
        db.session.delete(articleTypeSetting)
    db.session.delete(articleType)
    try:
        db.session.commit()
    except:
        db.session.roolback()
        flash(u'删除分类失败', 'danger')
    else:
        flash(r'删除分类成功！同时将原来该分类的%s 篇博文添加到<未分类>。'% count, 'success')
    return redirect(url_for('admin.manage_articleTypes', page=page))

@admin.route('/manage-articleTypes/nav/sort-up/<int:id>')
@login_required
def nav_sort_up(id):
    page = request.args.get('page', 1, type=int)
    menu =Menu.query.get_or_404(id)
    pre_menu = Menu.query.filter_by(order=menu.order-1).first()
    if pre_menu:
        (menu.order, pre_menu.order)=(pre_menu.order, menu.order)
        db.session.add(menu)
        db.session.add(pre_menu)
        db.session.commit()
        flash(u'成功将该导航升序！','success')
    else:
        flash(u'该导航已经位于最前面！', 'danger')

    return redirect(url_for('admin.manage_articleTypes_nav', page=page))

@admin.route('/manage-articleTypes/nav/sort-down/<int:id>')
@login_required
def nav_sort_down(id):
    page = request.args.get('page',1,type=int)

    menu = Menu.query.get_or_404(id)
    latter_menu = Menu.query.filter_by(order=menu.order+1).first()
    if latter_menu:
        (latter_menu.order,menu.order)=(menu.order, latter_menu.order)
        db.session.add(menu)
        db.session.add(latter_menu)
        db.session.commit()
        flash(u'成功将导航降序')
    else:
        flash(u'该导航已经位于最后面','danger')
    return redirect(url_for('admin.manage_articleTypes_nav', page=page))



@admin.route('/manage-articleTypes/get-articleTypeNav-info/<int:id>')
@login_required
def get_articleTypeNav_info(id):
    if request.is_xhr:
        menu = Menu.query.get_or_404(id)
        return jsonify({
            'name':menu.name,
            'nav_id': menu.id,
        })

@admin.route('manage-articleTypes/nav/edit-nav', methods=['GET','POST'])
@login_required
def edit_nav():
    form2=EditArticleNavTypeForm()

    page = request.args.get('page', 1, type=int)

    if form2.validate_on_submit():
        name = form2.name.data
        nav_id = int(form2.nav_id.data)
        if Menu.query.filter_by(name=name).first() \
                and Menu.query.filter_by(name=name).first().id != nav_id:
            flash(u'修改导航失败！该导航名称已经存在。', 'danger')
        else:
            nav = Menu.query.get_or_404(nav_id)
            nav.name = name
            db.session.add(nav)
            db.session.commit()
            flash(u'修改导航成功！', 'success')
        return redirect(url_for('admin.manage_articleTypes_nav', page=page))
    if form2.errors:
        flash(u'修改导航失败！请查看填写有无错误。', 'danger')
        return redirect(url_for('admin.manage_articleTypes_nav', page=page))


@admin.route('/manage-articletypes/nav/delete-nav/<int:id>')
@login_required
def delete_nav(id):
    page = request.args.get('page',1,type=int)
    nav = Menu.query.get_or_404(id)
    count=0
    for articleType in nav.types.all():
        count += 1
        articleType.menu=None
        db.session.add(articleType)
    nav.sort_delete()
    db.session.delete(nav)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash(u'导航删除失败', 'danger')
    else:
        flash(u'删除导航成功！同时将原来该导航的%s 的分类的导航设置为无' % count,'success')
    return redirect(url_for('admin.manage_articleTypes_nav', page=page))




