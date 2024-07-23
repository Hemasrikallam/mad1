from flask import Flask, render_template, request, redirect, url_for,session
import sqlite3
import os
import logging
from flask import jsonify
app = Flask(__name__)

# Function to create the User table (execute only once)
def create_user_table():
    try:
        connection = sqlite3.connect('mad1_db.db')
        cursor = connection.cursor()

        connection.commit()
        connection.close()
        print("Database connected and User table created successfully.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

# Create the User table before running the app
create_user_table()
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/lib_login', methods=['GET', 'POST'])
def lib_login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']

        # Check if the user exists in the User table
        try:
            connection = sqlite3.connect('mad1_db.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM lib WHERE name = ? AND password = ?', (name, password))
            user = cursor.fetchone()
            connection.close()

            if user:
                return redirect(url_for('lib_dashboard')) 
            else:
               return "Login failed. Please login again <a href='" + url_for('lib_login') + "'>login_again</a>."
        except Exception as e:
            print(f"Error checking user in the database: {e}")

    return render_template('librarian/lib_login.html')
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        
        # Check if the user exists in the User table
        try:
            connection = sqlite3.connect('mad1_db.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM User WHERE name = ? AND password = ?', (name, password))
            user = cursor.fetchone()
            connection.close()

            if user:
                 return redirect(url_for('user_dashboard',name=name))
            else:
               return "Login failed. Please <a href='" + url_for('registration') + "'>register</a>."
        except Exception as e:
            print(f"Error checking user in the database: {e}")

    return render_template('user/user_login.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']

     
        try:
            connection = sqlite3.connect('mad1_db.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO User (name, password) VALUES (?, ?)', (name, password))
            connection.commit()
            connection.close()
            print("User added to the database.")
            return redirect(url_for('user_login')) 
        except Exception as e:
            print(f"Error adding user to the database: {e}")

    return render_template('registration.html')
@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():   
    name = request.args.get('name')
    connection = sqlite3.connect('mad1_db.db')
    cursor = connection.cursor()

    # Fetch all records from the books table
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()

    connection.close()

    if books:
        return render_template('user/user_dashboard.html', books=books,name=name)
    else:
        return render_template('user/user_dashboard.html', books=[])
@app.route('/book_details/<int:id>/<name>', methods=['GET', 'POST'])
def book_details(id,name):
        
    
        connection = sqlite3.connect('mad1_db.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM book_id WHERE id =?', (id,))
        book = cursor.fetchone()

        connection.close()

        if book:
            return render_template('user/book_details.html', book=book,name=name)
        else:
            return render_template('book_not_found.html')
@app.route('/lib_dashboard', methods =['GET','POST'] )
def lib_dashboard():
    if request.method=='POST':
        if 'title' in request.form and 'author' in request.form and 'image' in request.form:
            title = request.form['title']
            author = request.form['author']
            image = request.form['image']

            # Establish database connection
            connection = sqlite3.connect('mad1_db.db')
            cursor = connection.cursor()

            # Insert book details
            cursor.execute('INSERT INTO books (title, author, image) VALUES (?, ?, ?)', (title, author, image))
            connection.commit()

            # Get the ID of the newly added book
            book_id = cursor.lastrowid

            # Close database connection
            connection.close()

            return redirect(url_for('lib_addbook', id=book_id))
        
        elif 'selected_username' in request.form:
            selected_username = request.form.get('selected_username')

            connection = sqlite3.connect('mad1_db.db')
            cursor = connection.cursor()

            # Fetch book details issued to the selected username
            cursor.execute('SELECT * FROM book_issue WHERE username = ?', (selected_username,))
            book_issues = cursor.fetchall()

            connection.close()
            return render_template('librarian/lib_dashboard.html', book_issues=book_issues, selected_username=selected_username)

        elif 'delete_book' in request.form:
            # Establish database connection
            connection = sqlite3.connect('mad1_db.db')
            cursor = connection.cursor()

            # Get the book ID to delete
            book_id = request.form['delete_book']

            # Delete the book from the database
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            connection.commit()

            # Close database connection
            connection.close()

            return redirect(url_for('lib_dashboard'))
        users = User.query.all()
        books = Book.query.all()
       
    connection = sqlite3.connect('mad1_db.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    cursor.execute('SELECT * FROM User')
    users = cursor.fetchall()
    connection.close()
    return render_template('librarian/lib_dashboard.html',books=books,users=users)

@app.route('/request_lib',methods=['GET','POST'])
def request_lib():
    if request.method == 'POST':
        lib_book_id = request.form['lib-book-id']
        username = request.form['username']
        access_time = request.form['access-time']
        connection = sqlite3.connect('mad1_db.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO book_issue (book_id,username,access) VALUES (?,?,?)', (lib_book_id,username,access_time))
        connection.commit()
        connection.close()
        
       
        return redirect(url_for('user_dashboard')) 
    connection = sqlite3.connect('mad1_db.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    cursor.execute('SELECT * FROM User')
    users = cursor.fetchall()
    connection.close()
    return render_template('librarian/request_lib.html',books=books,users=users)
    
logging.basicConfig(level=logging.DEBUG)
@app.route('/request_book', methods=['POST'])
def request_book():
    data = request.json
    logging.debug("Request data: %s", data)
    
    book_id = data.get('book_id')
    username = data.get('username')
    access_duration=data.get('access_duration')
    connection = sqlite3.connect('mad1_db.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO book_issue (book_id,username,access) VALUES (?,?,?)', (book_id,username,access_duration))
    connection.commit()
    connection.close()
    return jsonify({'message': 'check view_details'})
    
@app.route('/return_book', methods=['POST'])
def return_book():
    data = request.json
    
    book_id = data.get('book_id')
    username = data.get('username')
    connection = sqlite3.connect('mad1_db.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM book_issue WHERE (book_id, username) = (?, ?)', (book_id, username))
    connection.commit()
    connection.close()
    return jsonify({'message': 'view_details returned'})

@app.route('/lib_addbook/<int:id>', methods =['GET','POST'])
def lib_addbook(id):
    if request.method=='POST':
        details = request.form['details']
        title1 = request.form['title1'] 
        author1=request.form['author1'] 
        connection = sqlite3.connect('mad1_db.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO book_id (id,details, title1,author) VALUES (?,?, ?, ?)', (id,details, title1,author1))
        connection.commit()
        connection.close()
        print("e-book details added to the database.")
        return 'book deatils added'
    return render_template('librarian/lib_addbook.html',id=id)
@app.route('/lib_edit/<int:book_id>', methods=['GET', 'POST'])
def lib_edit(book_id):
    if request.method=='POST':
        ti=request.form['ti']
        au=request.form['au']
        i=request.form['i']
                        
        connection = sqlite3.connect('mad1_db.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE books SET title = ?,author=?,image=? WHERE id = ?', (ti,au,i, book_id))
        connection.commit()

        connection.close()

        return redirect(url_for('lib_edit',book_id=book_id))
        
    
    # Fetch book details for the given book ID
    connection = sqlite3.connect('mad1_db.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    
    book = cursor.fetchone()
    connection.close()

    return render_template('librarian/lib_edit.html', book=book,book_id=book_id)
@app.route('/lib_editmore/<int:book_id1>', methods=['GET','POST'])
def lib_editmore(book_id1):
    if request.method == 'POST':
        details3=request.form['details3']
        title3=request.form['title3']
        author3=request.form['author3']
        connection=sqlite3.connect('mad1_db.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE book_id  SET details = ?,title1=?,author=? WHERE id = ?', (details3,title3,author3, book_id1))
        connection.commit()
        connection.close()
        return redirect(url_for('lib_editmore',book_id1=book_id1))
    connection=sqlite3.connect('mad1_db.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM book_id WHERE id = ?', (book_id1,))
    
    book = cursor.fetchone()
    connection.close()

    return render_template('librarian/lib_editmore.html', book=book,book_id1=book_id1)
    
    
                                                        

if __name__ == '__main__':
    app.run(debug=True)
