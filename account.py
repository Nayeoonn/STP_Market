from flask import Blueprint, flash, url_for
from flask import render_template, request, redirect, session, jsonify
from model import User,  db

blue_account = Blueprint("account", __name__, url_prefix="/account")

@blue_account.route("/register", methods=('GET', 'POST'))
def register() : 
    if request.method == 'POST':
        userid = request.form['id']
        password = request.form['pw']
        check_password = request.form['check_pw']
        
        if password == check_password:
            usertable = User.query.filter_by(userid=userid).first()
            if not usertable : 
                usertable=User(userid, password)
                db.session.add(usertable)
                db.session.commit()
                flash('가입을 축하합니다!')   
                return render_template("login.html")
            else :
                flash("이미 존재하는 아이디입니다.")
        else:
            flash("패스워드가 일치하지 않습니다.")
        
    return render_template("register.html")
    
@blue_account.route("/login", methods=('GET', 'POST'))
def login() : 
    if request.method == 'POST':
        userid = request.form['id']
        password = request.form['pw']

        usertable = User.query.filter_by(userid=userid).first()
        if usertable : 
            if usertable.check_password(password) : 
                flash("환영합니다.")
                session['userid'] = userid
                return redirect("/")
            
        flash("아이디 또는 비밀번호를 확인해주세요.")        
        
    return render_template("login.html")
        
@blue_account.route("/logout")
def logout():
    if session.get('userid'): 
        session.pop('userid', None)
        flash('로그아웃이 완료되었습니다.')
        return redirect('/') 
    
@blue_account.route("/userpage/<userid>")
def mypage(userid):
    if session.get('userid'):
        current_user = User.query.filter_by(userid=session.get('userid')).first()
        user = User.query.filter_by(userid=userid).first()
        print("mypage user: ", user)
        is_follow = True if current_user.is_following(user) else False
        products = user.products
        follow_products = user.follow_products()
        print("followlist: ",user.followerlist() , user.followed.all())
        print(follow_products)
        followerlist = user.followerlist()
        return render_template('mypage.html', user=user, products=products, follow_products=follow_products, followerlist=followerlist, is_follow=is_follow)
    else:
        flash('로그인 해주세요')
        return render_template('login.html')

@blue_account.route('/follow/<userid>')
def follow(userid):
    message = ""
    is_follow = False

    current_userid = session.get("userid")
    if not current_userid: 
        flash('로그인부터 해주세요')
        return redirect(url_for('account.login'))
    

    user = User.query.filter_by(userid=userid).first()
    current_user = User.query.filter_by(userid=current_userid).first()
    if user is None:
        message= '{}님을 찾을 수 없습니다.'.format(userid)

    elif user == current_user:
        message = '본인은 팔로우할 수 없습니다.'
    else: 

        if current_user.is_following(user):

            is_follow = False
            current_user.unfollow(user)
            

        else: 
            # 상대 유저 팔로우
            is_follow = True
            current_user.follow(user)
            
        db.session.commit()
    
    return jsonify({"message" : message, "is_follow": is_follow})
