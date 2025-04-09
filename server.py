from flask import Flask, render_template, request, redirect, url_for, abort
import psycopg2

app = Flask(__name__, static_folder="")


class User:
    
    def __init__ (self, user_order, user_name, mail, password):
        self.user_order = user_order
        self.user_name = user_name
        self.mail = mail
        self.password = password
users = []
    
@app.route('/reg')
def reg():
    return render_template('reg.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/')
def main():
    return render_template('main.html')


@app.route('/user/create', methods=['POST'])
def create_user():
    user_name = request.form['user_name']
    mail = request.form['mail']
    password = request.form['password']
    
    connection = psycopg2.connect(database='users_application', user='postgres',
                                  password='123123', host='localhost', port='5432')
    
    cursor = connection.cursor()
    
    cursor.execute('''INSERT INTO USERS(user_name, mail, password)
                   VALUES (%s, %s, %s);''', (user_name, mail, password))
    
    connection.commit()
    connection.close()
    cursor.close()
    
    return redirect(url_for('success'))

@app.route('/users/all')    
@app.route('/user/<int:user_id>')
def get_user(user_id=None):
    connection = psycopg2.connect(database='users_application', user='postgres',
                                  password='123123', host='localhost', port='5432')

    cursor = connection.cursor()
    
    if user_id is None:
        cursor.execute('''SELECT user_order, user_name, mail, password FROM USERS''')
        users_data = cursor.fetchall()
        connection.close()
        cursor.close()
        
        return [User(i[0], i[1], i[2], i[3]).__dict__ for i in users_data]
    
    cursor.execute('''SELECT * FROM USERS WHERE users_order=%s''', [user_id])
    
    user_data = cursor.fetchall()
    
    connection.close()
    cursor.close
    
    if users_data.__len__():
        return abort(404, f"User with id {user_id} not found")
    
    return User(user_data[0][0], user_data[0][1]).__dict__

if __name__ == '__main__':
    app.run()