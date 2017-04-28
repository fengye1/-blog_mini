#coding:utf-8


from datetime import datetime
import json
from flask import request,render_template

from . import admin
from flask_login import login_required,current_user


@admin.route('/sumbit-articles', methods=['GET','POST'])
@login_required
def submitArticles():
    print('abc')
    return render_template('admin/admin_base.html')


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






