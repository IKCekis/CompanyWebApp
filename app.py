from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import os
from datetime import date
import hashlib
import sqlite3
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

today = date.today()
app = Flask(__name__)
app.config['SECRET_KEY'] = "<write_youR_secret_key>" #fill here with secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CompanyName = "CompanyName"
admin_name="Admin" #default username
admin_pass="Admin" #default password
admin_hash=hashlib.md5(admin_pass.encode()).hexdigest()
admin_mail="info@ikcekis.com" #dump mail address
@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM Users WHERE UserID = ?", [user_id])
    values = cursor.fetchone()
    user = User()
    user.id = values[0]
    user.user_name = values[1]
    user.hash = values[2]
    user.mail = values[3]
    return user

# server = '<write your db server address>'
# database = 'Customer' #write your db name
# username = '<username>' #write your db username
# password = '<password>' #write your db password
# cnxn = pyodbc.connect(
#     'DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password) #Connection string
# cursor = cnxn.cursor()

DATABASE = os.getcwd()+"/static/"

cnxn = sqlite3.connect(DATABASE+"database.db", check_same_thread=False)
cursor = cnxn.cursor()

try:
    print("Customer database is creating...")
    cursor.execute(
        """CREATE TABLE Customers (CustomerID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, CompanyName varchar(255), City varchar(255), PhoneNum varchar(255), Email varchar(255)); """)
    cnxn.commit()
    print("Customer database is created successfully!")
except sqlite3.OperationalError:
    print("A problem was encountered while creating Customer database!")

try:
    print("Users database is creating...")
    cursor.execute(
        """CREATE TABLE Users (UserID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, UserName varchar(255) NOT NULL UNIQUE , Password varchar(255) NOT NULL, UserMail varchar(255) NOT NULL UNIQUE ); """)
    cnxn.commit()
    print("Users database is created successfully!")
except sqlite3.OperationalError:
    print("A problem was encountered while creating Customer database!")

cursor.execute("SELECT * FROM Users")
is_user = cursor.fetchone()
if is_user:
    print("Admin User Already Created!")
else:
    data = [(admin_name, admin_hash, admin_mail)]
    cursor.executemany("INSERT INTO Users(UserName, Password, UserMail) VALUES (?, ?, ?)", data)
    cnxn.commit()
    print("Admin User Created Successfully")

try:
    print("Products database is creating...")
    cursor.execute(
        """CREATE TABLE Products (ProductID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, ProductName varchar(255) UNIQUE , StockNum int);""")
    cnxn.commit()
    print("Products database is created successfully!")
except sqlite3.OperationalError:
    print("A problem was encountered while creating Products database!")

try:
    print("Orders database is creating...")
    cursor.execute(
        """CREATE TABLE Orders (OrderNo INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, CompanyName varchar(255),ProductName varchar(255), SaleDate varchar(255), SaleNum int, Price int);""")
    cnxn.commit()
    print("Orders database is created successfully!")
except sqlite3.OperationalError:
    print("A problem was encountered while creating Orders database!")

customersDB = "Customers"
productsDB = "Products"
ordersDB = "Orders"
customersDB_ID = "CustomerID"
productsDB_ID = "ProductID"
ordersDB_ID = "OrderNo"
path = os.getcwd()
bg = "#0E2336"
fg = "#CB9863"
name_str = "Şirket Adı"
city_str = "Şehir"
num_str = "Telefon Numarası"
mail_str = "Email"
name_prod = "Ürün Adı"
stock_prod = "Ürün Adedi"
date_sale = "Tarih"
sale_price = "Adet Fiyatı"

class User(UserMixin):
    def __int__(self, user_id, user_name, user_hash, mail):
        self.id = user_id
        self.user_name = user_name
        self.hash= user_hash
        self.mail = mail

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

def getFromDBSingle(query, data=None):
    if data:
        cursor.execute(query, [data])
    else:
        cursor.execute(query)
    table_values = []
    for i in cursor.fetchall():
        table_values.append(i)
        print(table_values)
    return table_values

def getFromDBMany(query, data):
    cursor.executemany(query, data)
    table_values = []
    for i in cursor.fetchall():
        table_values.append(i)
        print(table_values)
    return table_values

def runOnDBSingle(query):
    cursor.execute(query)
    cnxn.commit()

def runOnDBMany(query, data):
    cursor.executemany(query, data)
    cnxn.commit()

@app.route('/', methods=['POST', 'GET'])
def index():  # put application's code here
    return redirect(url_for('login'))

@app.route('/companies', methods=['POST', 'GET'])
@login_required
def companies():
    title = f"{CompanyName} şirketler"
    query = "SELECT * FROM Customers"
    table = getFromDBSingle(query)
    if table:
        print(table[0])
        length = len(table)
        return render_template('companies.html', table=table, length=length, title=title)
    else:
        flash("Hiç Veri Bulunamadı!")
        return render_template('companies.html', title=title)

@app.route('/products', methods=['POST', 'GET'])
@login_required
def products():
    title = f"{CompanyName} Ürünler"
    query = "SELECT * FROM Products"
    table = getFromDBSingle(query)
    length = len(table)
    return render_template('products.html', table=table, length=length, title=title)

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    title = f"{CompanyName} Ara"
    if request.method == 'POST':
        looking_for = request.form.get('looking_for')
        looking_for = '%' + looking_for + '%'
        query = f"SELECT Customers.CompanyName, Orders.ProductName, Customers.PhoneNum, Customers.Email, Orders.SaleDate, Orders.SaleNum, Orders.Price FROM Customers JOIN Orders ON Customers.CompanyName = Orders.CompanyName WHERE Customers.CompanyName LIKE ? OR Orders.ProductName LIKE ? OR Customers.PhoneNum LIKE ? OR Customers.Email LIKE ?"
        data = [(looking_for, looking_for, looking_for, looking_for)]
        table = getFromDBMany(query, data)
        print(table)
        return render_template('search.html', table=table, title=title, length=len(table))
    return redirect(url_for('index'))

@app.route('/sales', methods=['POST', 'GET'])
@login_required
def sales():
    title = f"{CompanyName} Satışlar"
    query = "SELECT * FROM Orders"
    table = getFromDBSingle(query)
    query = "SELECT CompanyName FROM Customers"
    company = getFromDBSingle(query)
    query = "SELECT ProductName FROM Products"
    product = getFromDBSingle(query)
    length = len(table)
    print(company)
    print(product)
    return render_template('sales.html', table=table, length=length, title=title, today=today, company=company, product=product)

@app.route('/register', methods=["POST", "GET"])
@login_required
def register():
    title = f"{CompanyName} Kayıt Ol"
    error = ""
    conf_error = ""
    if request.method == 'POST':
        mail = request.form.get("email")
        user_name = request.form.get("user_name")
        password = hashlib.md5(request.form.get("user_pass").encode()).hexdigest()
        password_conf = hashlib.md5(request.form.get("user_pass_conf").encode()).hexdigest()
        is_unique = 1
        query = "SELECT UserName, UserMail FROM Users"
        users = getFromDBSingle(query)
        for i in range(0, len(users)):
            if user_name == users[i][0]:
                is_unique = 0
                error = "Kullanıcı adı daha önce kullanılmış"
            if mail == users[i][1]:
                is_unique = 0
                error = "Email adresi daha önce kullanılmış!"
        if is_unique and mail != "" and user_name != "" and request.form.get("user_pass") != "":
            if password == password_conf:
                query = "INSERT INTO Users(UserName, Password, UserMail) VALUES (?, ?, ?)"
                data = [(user_name, password, mail)]
                runOnDBMany(query, data)
            else:
                conf_error = "Şifreler aynı olmalıdır"
    return render_template('register.html', title=title, error=error, conf_error=conf_error)

#Company
@app.route('/add_company', methods=['POST', 'GET'])
@login_required
def add_comp():
    if request.method == 'POST':
        name = request.form.get('comp_name')
        city = request.form.get('city')
        num = request.form.get('phone_num')
        mail = request.form.get('comp_mail')

        if name == "" or name == None:
            flash(f"{name_str} boş bırakılamaz!")
            return redirect(url_for('companies'))
        if city == "" or city == None:
            flash(f"{city_str} boş bırakılamaz!")
            return redirect(url_for('companies'))
        if num == "" or num == None:
            flash(f"{num_str} boş bırakılamaz!")
            return redirect(url_for('companies'))
        if mail == "" or mail == None:
            flash(f"{mail_str} boş bırakılamaz!")
            return redirect(url_for('companies'))

        query = "INSERT INTO Customers (CompanyName, City, PhoneNum, Email) VALUES (?, ?, ?, ?)"
        data = [(name, city, num, mail)]
        cursor.executemany(query, data)
        cnxn.commit()
        return redirect(url_for('companies'))
    return redirect(url_for('companies'))

@app.route('/delete_company', methods=['POST', 'GET'])
@login_required
def delete_comp():
    if request.method == 'POST':
        selected = request.form.get('select')
        print(selected)
        query = f"DELETE FROM {customersDB} WHERE {customersDB_ID} = ?"
        data = [selected]
        cursor.execute(query, data)
        cnxn.commit()
        return redirect(url_for('companies'))
    return redirect(url_for('companies'))

class Products():
    def __init__(self, prod_name, total_sale, average_price):
        self.prod_name = prod_name
        self.total_sale = total_sale
        self.average_price = average_price

@app.route('/details_company/<int:comp_id>', methods=['POST', 'GET'])
@login_required
def details_comp(comp_id):
    title = f"{CompanyName} Düzenle"
    if request.method == 'POST':
        name = request.form.get('comp_name')
        city = request.form.get('city')
        num = request.form.get('phone_num')
        mail = request.form.get('comp_mail')

        query = "UPDATE Customers SET CompanyName=?, City=?, PhoneNum=?, Email=? WHERE CustomerID = ?"
        data = [(name, city, num, mail, comp_id)]
        cursor.executemany(query, data)
        cnxn.commit()

        return redirect(url_for('companies'))

    if comp_id:
        query = "SELECT * FROM Customers WHERE CustomerID = ?"
        data1 = comp_id
        table = getFromDBSingle(query, data1)
        print(table)
        query = "SELECT ProductName FROM Orders WHERE CompanyName=?"
        data2 = table[0][1]
        raw_values = getFromDBSingle(query, data2)
        products = []
        proper_list = []
        for i in range(len(raw_values)):
            if raw_values[i][0] in products:
                pass
            else:
                products.append(raw_values[i][0])
        for p in products:
            list = []
            total = 0
            average = 0
            query = "SELECT SaleNum, Price FROM Orders WHERE ProductName = ?"
            data = p
            values = getFromDBSingle(query, data)
            for i in range(0, len(values)):
                total += values[i][0]
                average = average + (values[i][0] * values[i][1])
            average = average / total
            list.append(p)
            list.append(total)
            list.append(average)
            proper_list.append(list)
        print(len(proper_list))
        print(proper_list)
        if table:
            print(table)
            return render_template('details.html', title=title, table=table, length=len(table), comp_id=comp_id, detail_table=proper_list, detail_length=len(proper_list))
    else:
        flash("Böyle bir şirket bulunamadı!")
        return redirect(url_for('companies'))

#Products
@app.route('/add_product', methods=['POST', 'GET'])
@login_required
def add_prod():
    if request.method == 'POST':
        name = request.form.get('prod_name')
        stock_num = request.form.get('stock_num')
        if not stock_num.isdigit():
            flash(f"Depo Sayısı bir sayı olmalıdır!")
            return redirect('products')

        if name == "" or name == None:
            flash(f"{name_prod} boş bırakılamaz!")
            return redirect(url_for('products'))
        if stock_num == "" or stock_num == None:
            flash(f"{stock_prod} boş bırakılamaz!")
            return redirect(url_for('products'))


        query = "INSERT INTO Products (ProductName, StockNum) VALUES (?, ?)"
        data = [(name, stock_num)]
        cursor.executemany(query, data)
        cnxn.commit()
        return redirect(url_for('products'))
    return redirect(url_for('products'))

@app.route('/delete_products', methods=['POST', 'GET'])
@login_required
def delete_prod():
    if request.method == 'POST':
        selected = request.form.get('select')
        print(selected)
        query = f"DELETE FROM {productsDB} WHERE {productsDB_ID} = ?"
        data = [selected]
        cursor.execute(query, data)
        cnxn.commit()
        return redirect(url_for('products'))
    return redirect(url_for('products'))

@app.route('/details_products/<int:prod_id>', methods=['POST', 'GET'])
@login_required
def details_prod(prod_id):
    title = f"{CompanyName} Düzenle"
    if request.method == 'POST':
        name = request.form.get('prod_name')
        stock_num = request.form.get('stock_num')
        if not stock_num.isdigit():
            flash(f"Depo Sayısı bir sayı olmalıdır!")
            return redirect('details_prod', prod_id=prod_id)

        query = "UPDATE Products SET ProductName=?, StockNum=? WHERE ProductID = ?"
        data = [(name, stock_num, prod_id)]
        cursor.executemany(query, data)
        cnxn.commit()

        return redirect(url_for('products'))

    if prod_id:
        query = "SELECT * FROM Products WHERE ProductID = ?"
        data = prod_id
        table = getFromDBSingle(query, data)
        query = "SELECT CompanyName From Orders WHERE ProductName = ?"
        data2 = table[0][1]
        raw_values = getFromDBSingle(query, data2)
        companies = []
        proper_list = []
        for i in range(len(raw_values)):
            if raw_values[i][0] in companies:
                pass
            else:
                companies.append(raw_values[i][0])
        for c in companies:
            list = []
            total = 0
            average = 0
            query = "SELECT Customers.PhoneNum, Orders.SaleNum, Orders.Price FROM Customers JOIN Orders ON Customers.CompanyName = Orders.CompanyName WHERE Orders.CompanyName = ? AND Orders.ProductName = ?"
            data = (c, table[0][1])
            cursor.execute(query, data)
            values = []
            for i in cursor.fetchall():
                values.append(i)
            for i in range(0, len(values)):
                phone = values[i][0]
                total += values[i][1]
                average = average + (values[i][1] * values[i][2])
            average = average / total
            list.append(c)
            list.append(phone)
            list.append(total)
            list.append(average)
            proper_list.append(list)
        print(len(proper_list))
        print(proper_list)
        if table:
            print(table)
            return render_template('details.html', title=title, table=table, length=len(table), prod_id=prod_id, detail_table=proper_list, detail_length=len(proper_list))
    else:
        flash("Böyle bir ürün bulunamadı!")
        return redirect(url_for('products'))

#Sales
@app.route('/add_sale', methods=['POST', 'GET'])
@login_required
def add_sale():
    if request.method == 'POST':
        comp_name = request.form.get('comp_name')
        query = "SELECT * FROM Customers WHERE CompanyName = ?"
        data = [comp_name]
        cursor.execute(query, data)
        company = cursor.fetchone()
        if not company:
            flash("Şirket bulunamadı, lütfen önce şirketi eklemeyi deneyin!")
            return redirect('companies')
        prod_name = request.form.get('prod_name')
        query = "SELECT * FROM Products WHERE ProductName = ?"
        data = [prod_name]
        cursor.execute(query, data)
        product = cursor.fetchone()
        if not product:
            flash("Ürün bulunamadı, lütfen önce ürünü eklemeyi deneyin!")
            return redirect('products')
        sale_date = request.form.get('sale_date')
        sale_num = request.form.get('sale_num')
        price = request.form.get('price')

        if comp_name == "" or comp_name == None:
            flash(f"{name_str} boş bırakılamaz!")
            return redirect('sales')

        if prod_name == "" or prod_name == None:
            flash(f"{prod_name} boş bırakılamaz!")
            return redirect('sales')

        if sale_date == "" or sale_date == None:
            flash(f"{date_sale} boş bırakılamaz!")
            return redirect('sales')

        if sale_num == 0 or sale_num == None:
            flash(f"{prod_name} boş bırakılamaz!")
            return redirect('sales')

        if price == 0 or price == None:
            flash(f"{prod_name} boş bırakılamaz!")
            return redirect('sales')

        if int(sale_num) <= 0:
            flash(f"Satış Adedi sıfırdan küçük veya eşit olamaz!")
            return redirect('sales')

        if int(price) <= 0:
            flash(f"{sale_price} sıfırdan küçük veya eşit olamaz!")
            return redirect('sales')

        query = "INSERT INTO Orders (CompanyName, ProductName, SaleDate, SaleNum, Price) VALUES (?, ?, ?, ?, ?)"
        data = [(comp_name, prod_name, sale_date, sale_num, price)]
        cursor.executemany(query, data)
        cnxn.commit()
        query = "SELECT StockNum FROM Products WHERE ProductName=?"
        data = [prod_name]
        cursor.execute(query, data)
        stock = cursor.fetchone()

        stock = stock[0] - int(sale_num)
        query = "UPDATE Products SET StockNum = ? WHERE ProductName = ?"
        data = [(stock, prod_name)]
        cursor.executemany(query, data)
        cnxn.commit()
        return redirect(url_for('sales'))
    return redirect(url_for('sales'))

@app.route('/delete_sales', methods=['POST', 'GET'])
@login_required
def delete_sale():
    if request.method == 'POST':
        selected = request.form.get('select')
        print(selected)
        query = f"DELETE FROM {ordersDB} WHERE {ordersDB_ID} = ?"
        data = [selected]
        cursor.execute(query, data)
        cnxn.commit()
        return redirect(url_for('sales'))
    return redirect(url_for('sales'))

@app.route('/details_sales/<int:sale_id>', methods=['POST', 'GET'])
@login_required
def details_sale(sale_id):
    title = f"{CompanyName} Düzenle"
    if request.method == 'POST':
        comp_name = request.form.get('comp_name')
        prod_name = request.form.get('prod_name')
        sale_date = request.form.get('sale_date')
        sale_num = request.form.get('sale_num')
        price = request.form.get('price')

        if request.method == 'POST':
            comp_name = request.form.get('comp_name')
            query = "SELECT * FROM Customers WHERE CompanyName = ?"
            data = [comp_name]
            cursor.execute(query, data)
            company = cursor.fetchone()
            if not company:
                flash("Şirket bulunamadı, lütfen önce şirketi eklemeyi deneyin!")
                return redirect('companies')
            prod_name = request.form.get('prod_name')
            query = "SELECT * FROM Products WHERE ProductName = ?"
            data = [prod_name]
            cursor.execute(query, data)
            product = cursor.fetchone()
            if not product:
                flash("Ürün bulunamadı, lütfen önce ürünü eklemeyi deneyin!")
                return redirect('products')
            sale_date = request.form.get('sale_date')
            sale_num = request.form.get('sale_num')
            price = request.form.get('price')

            if comp_name == "" or comp_name == None:
                flash(f"{name_str} boş bırakılamaz!")
                return redirect('details_sale', sale_id=sale_id)

            if prod_name == "" or prod_name == None:
                flash(f"{prod_name} boş bırakılamaz!")
                return redirect('details_sale', sale_id=sale_id)

            if sale_date == "" or sale_date == None:
                flash(f"{date_sale} boş bırakılamaz!")
                return redirect('details_sale', sale_id=sale_id)

            if sale_num == 0 or sale_num == None:
                flash(f"Satış adedi boş bırakılamaz!")
                return redirect('details_sale', sale_id=sale_id)

            if price == 0 or price == None:
                flash(f"{sale_price} boş bırakılamaz!")
                return redirect('details_sale', sale_id=sale_id)

            if int(sale_num) <= 0:
                flash(f"Satış Adedi sıfırdan küçük veya eşit olamaz!")
                return redirect('details_sale', sale_id=sale_id)

            if int(price) <= 0:
                flash(f"{sale_price} sıfırdan küçük veya eşit olamaz!")
                return redirect('details_sale', sale_id=sale_id)

        query = "SELECT SaleNum FROM Orders WHERE ProductName=?"
        data = [prod_name]
        cursor.execute(query, data)
        old_num = cursor.fetchone()
        query = "UPDATE Orders SET CompanyName = ?, ProductName = ?, SaleDate = ?, SaleNum = ?, Price = ? WHERE OrderNo = ?"
        print(comp_name, prod_name, sale_date, sale_num, price, sale_id)
        data = [(comp_name, prod_name, sale_date, sale_num, price, sale_id)]
        cursor.executemany(query, data)
        cnxn.commit()
        query = "SELECT StockNum FROM Products WHERE ProductName=?"
        data = [prod_name]
        cursor.execute(query, data)
        stock = cursor.fetchone()
        stock = stock[0] - (int(sale_num) - int(old_num[0]))
        query = "UPDATE Products SET StockNum = ? WHERE ProductName = ?"
        data = [(stock, prod_name)]
        cursor.executemany(query, data)
        cnxn.commit()

        return redirect(url_for('products'))
    if sale_id:
        query = "SELECT * FROM Orders WHERE OrderNo = ?"
        data = sale_id
        table = getFromDBSingle(query, data)
        if table:
            print(table)
            return render_template('details.html', title=title, table=table, length=len(table), sale_id=sale_id)
    else:
        flash("Böyle bir satış bulunamadı!")
        return redirect(url_for('sales'))



@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    error = "Hesaptan çıkış yaptınız!"
    return redirect(url_for('login'))

@app.route('/login', methods=["POST", "GET"])
def login():
    title = f"{CompanyName} Giriş Yap"
    error = ""
    if current_user.is_authenticated:
        return redirect(url_for('companies'))
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_name = str(user_name)
        if(user_name != ""):
            password = hashlib.md5(request.form.get("user_pass").encode()).hexdigest()
            query = "SELECT * FROM Users WHERE UserName = ?"
            data = [user_name]
            cursor.execute(query, data)
            credentials = cursor.fetchone()
            if credentials:
                user = User()
                user.id = credentials[0]
                user.user_name = credentials[1]
                user.hash = credentials[2]
                user.mail = credentials[3]
                if user.hash == password:
                    #Login user here
                    login_user(user)
                    return redirect(url_for("index"))
                else:
                    error = "Yanlış kullanıcı adı veya şifre tekrar deneyin!"
            else:
                error = "Yanlış kullanıcı adı veya şifre tekrar deneyin!"

    return render_template('login.html', title=title, error=error)
if __name__ == '__main__':
    try:
        app.run()
    except Exception:
        flash("Bilinmeyen bir hata ile karşılaşıldı!")
        flash("Verilerin doğruluğunu kontrol ediniz!")
