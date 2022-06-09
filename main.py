import os
import time
from flask import Flask, render_template, session, url_for, request, redirect, flash
from model import User, Product, Image, db
import account

app = Flask(__name__)
app.secret_key = 'sample_secret'


app.register_blueprint(account.blue_account)


app.config['UPLOAD_FOLDER'] = 'static/upload/'


dbdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(dbdir, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
db.app = app
db.create_all()


def filesave(file):
    d_num = 1
    filename = file.filename
    file_path = app.config['UPLOAD_FOLDER'] + filename
    

    print(file_path, os.path.isfile(file_path))
    while os.path.isfile(file_path):
        filename =  str(d_num) + "_" + file.filename
        d_num += 1
        file_path = app.config['UPLOAD_FOLDER'] + filename
        
    file.save(file_path)
    return file_path



@app.route('/')
def index():
    products = Product.query.order_by(Product.is_sold, Product.id.desc()).all()

    return render_template('index.html', products=products)

@app.route('/search')
def search():
    keyword = request.args.get('keyword')
    if not keyword: return redirect('/')
    products = Product.query.filter(Product.keyword.contains(keyword)).all()
    print(products)
    return render_template('search.html', keyword=keyword, products=products)

@app.route('/write', methods=['GET', 'POST'])
def write():
    userid = session.get('userid')
    if userid: 
        if request.method == 'POST':
            userid = request.form['userid']
            price = request.form['price']
            keyword = request.form['keyword']
            description = request.form['description']
            create_date = str(time.strftime("%Y.%m.%d", time.localtime()))
            
            if price and keyword and description:
                user = User.query.filter_by(userid=userid).first()
                product = Product(price=price, keyword=keyword, description=description, create_date=create_date, user=user)
                db.session.add(product)
                

                files = request.files.getlist("file[]")

                if files[0].filename != '':

                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    for file in files:
                        file_path = filesave(file)
                        image = Image(file_path=file_path, product=product)
                        db.session.add(image)
                        
                db.session.commit()
                flash('작성 완료!')
                return redirect("/")
            else:
                flash('다시 입력해주세요')
                return render_template('write.html', userid=userid)
                
        return render_template('write.html', userid=userid)
            
    else:
        flash('로그인 해주세요')
        return redirect('/account/login')

 
@app.route('/modify/<int:id>',methods=['GET', 'POST'])
def modify(id):
    userid = session.get('userid')
    if userid: 
        product = Product.query.filter_by(id=id).first()

        if userid == product.user_id:
            if request.method == 'POST':
                price = request.form['price']
                keyword = request.form['keyword']
                description = request.form['description']
                
                if price and keyword and description:
                    product.price = price
                    product.keyword = keyword
                    product.description = description
                    print("product: ", product)
                    print("product price: ", product.price)
                    print("product keyword: ", product.keyword)
                    print("product descrption: ", product.description)

                    print("product images : ", product.images)
                    for image in product.images:
                        print("iamge: ", image)
                        if os.path.isfile(image.file_path):
                            os.remove(image.file_path)

                        db.session.delete(image)
                                

                    files = request.files.getlist("file[]")
                    print("new files: ", files)
                    if files[0].filename != '':

                        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                        

                        for file in files:
                            file_path = filesave(file)
                            image = Image(file_path=file_path, product=product)
                            db.session.add(image)
                            
                    db.session.commit()
                    flash('수정 완료!')
                    return redirect("/")
                

                else:
                    flash('다시 입력해주세요')
                    return render_template('modify.html', product=product, userid=product.user_id)
                    
            return render_template('modify.html', product=product, userid=product.user_id)

        else:
            flash('잘못된 접근입니다.')
            return redirect("/")
        

    else:
        flash('로그인 해주세요')
        return redirect('/account/login')


@app.route('/detail/<int:id>')
def detail(id):
    product = Product.query.filter_by(id=id).first()
    user = User.query.filter_by(userid=product.user_id).first()
    print(user)
    if product:
        return render_template('detail.html', product=product, user=user)
    else:
        flash('해당 제품은 없습니다.')
        return redirect('/')

@app.route('/payment/<int:id>')
def payment(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        product.is_sold = 1
        db.session.commit()
    else:
        flash('해당 제품은 없습니다.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)