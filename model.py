
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

followers = db.Table('followers',

    db.Column('follower_id', db.String, db.ForeignKey('user.userid')),

    db.Column('followed_id', db.String, db.ForeignKey('user.userid'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref="user")
    

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == userid),
        secondaryjoin=(followers.c.followed_id == userid),
        backref=db.backref('followers', lazy="dynamic"), lazy='dynamic')
    
    def __init__(self, userid, password):
        self.userid = userid
        self.set_password(password)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.password, password)
    

    def follow(self, user):
        if not self.is_following(user): # follow 상태가 아닌지 확인
            self.followed.append(user)  # user가 self에 follow
    

    def unfollow(self, user):
        if self.is_following(user):     # follow 상태인지 확인
            self.followed.remove(user)  # user가 self에 follow
    

    def is_following(self, user):

        return self.followed.filter(
            followers.c.followed_id == user.userid).count() > 0
    
    def followerlist(self):
        return self.followed.all()
    
    def followedlist(self):
        return self.follwers.all()
    
    def follow_products(self):

        follow_products = Product.query.join(

            followers, (followers.c.followed_id == Product.user_id)).filter(

                followers.c.follower_id == self.userid)
        return follow_products.all()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    keyword = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    create_date = db.Column(db.String(20), nullable=False)
    is_sold = db.Column(db.Integer, default=0)
    
    user_id = db.Column(db.String(50), db.ForeignKey("user.userid", ondelete="CASCADE"), nullable=False)
    images = db.relationship('Image', backref="product")

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
