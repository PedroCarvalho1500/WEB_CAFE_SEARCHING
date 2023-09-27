import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask_api import status
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
import requests
from wtforms import StringField, SubmitField, Label, PasswordField
from wtforms.validators import DataRequired, Length

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class SearchForCafeForm(FlaskForm):
    name = StringField(label='Name', validators=[Length(min=0, max=100)])
    location = StringField(label='Location', validators=[Length(min=0, max=100)])
    done = SubmitField('Search')



class AddCafeForm(FlaskForm):
    name = StringField(label='Name', validators=[Length(min=0, max=100)])
    map_url = StringField(label='Location URL', validators=[Length(min=0, max=100)])
    location = StringField(label='Location', validators=[Length(min=0, max=100)])
    img_url = StringField(label='IMG URL', validators=[Length(min=0, max=100)])
    seats = StringField(label='Number of Seats', validators=[Length(min=0, max=100)])
    has_toilet = StringField(label='Has Toilet? 1 for True and 0 for False', validators=[Length(min=1, max=1)])
    has_wifi = StringField(label='Has Wifi? 1 for True and 0 for False', validators=[Length(min=1, max=1)])
    has_sockets = StringField(label='Has Sockets? 1 for True and 0 for False', validators=[Length(min=1, max=1)])
    can_take_calls = StringField(label='Can Take Calls? 1 for True and 0 for False', validators=[Length(min=1, max=1)])
    coffee_price = StringField(label='Coffee Price Average', validators=[Length(min=0, max=10)])
    done = SubmitField('Save')


class DB_Actions():
    def __init__(self,title="",author="",rating=0):
        self.title = title
        self.author = author
        self.rating = rating

    def connect_db(self):
        self.conn = sqlite3.connect("instance/cafes.db")
        self.cursor = self.conn.cursor()

            
    def disconnect_db(self):
        print("DATABASE DISCONNECTED!!!")
        self.conn.close()

    def mountTables(self):
        self.connect_db()
        print("Conectando ao Banco de Dados!")
            
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS cafe (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(2000) UNIQUE NOT NULL,
                map_url VARCHAR(2000) NOT NULL,
                img_url VARCHAR(2000) NOT NULL,
                location VARCHAR(1000) NOT NULL,
                seats VARCHAR(1000) NOT NULL,
                has_toilet BOOLEAN NOT NULL,
                has_wifi BOOLEAN NOT NULL,
                has_sockets BOOLEAN NOT NULL,
                can_take_calls BOOLEAN NOT NULL,
                coffee_price VARCHAR(1000)
                )""")
                
        self.conn.commit()
        print("DATABASE CREATED!!!")
        self.disconnect_db()

    def get_random_cafe(self):
        self.connect_db()

        random_cafe = self.cursor.execute(""" SELECT * FROM cafe ORDER BY random() LIMIT 1""").fetchone()
        self.conn.commit()
        #input(random_cafe)

        self.disconnect_db()

        return random_cafe
    
    def get_all_cafes(self):
        self.connect_db()

        all_cafe = self.cursor.execute(""" SELECT * FROM cafe """).fetchall()
        self.conn.commit()
        #input(all_cafe)

        self.disconnect_db()

        return all_cafe

    def get_cafe_by_location(self,location):
        self.connect_db()

        all_cafe_by_location = self.cursor.execute(""" SELECT * FROM cafe WHERE location LIKE ?""", ["%"+location+"%"]).fetchall()
        self.conn.commit()
        #input(all_cafe_by_location)

        self.disconnect_db()

        return all_cafe_by_location
    
    def get_cafe_by_id(self,id):
        self.connect_db()

        all_cafe_by_id = self.cursor.execute(""" SELECT * FROM cafe WHERE id=?""", [id]).fetchall()
        self.conn.commit()
        #input(all_cafe_by_location)

        self.disconnect_db()

        return all_cafe_by_id

    def insert_new_cafe(self,name,map_url,img_url,location,has_sockets,has_toilet,has_wifi,can_take_calls,seats,coffee_price):
        self.connect_db()

        self.cursor.execute(""" INSERT INTO cafe (name,map_url,img_url,location,has_sockets,has_toilet,has_wifi,can_take_calls,seats,coffee_price) VALUES(?,?,?,?,?,?,?,?,?,?)""", (name,map_url,img_url,location,has_sockets,has_toilet,has_wifi,can_take_calls,seats,coffee_price))
        self.conn.commit()

        self.disconnect_db()

    def update_price(self,id,new_price):
        self.connect_db()

        self.cursor.execute(""" UPDATE cafe SET coffee_price=? WHERE id=?""", (new_price,id))
        self.conn.commit()

        self.disconnect_db()

    def delete_cafe(self,id):
        self.connect_db()

        self.cursor.execute(""" DELETE FROM cafe WHERE id=?""", [id])
        self.conn.commit()

        self.disconnect_db()

    def get_cafe_by_conditions(self,name,location):
        self.connect_db()

        self.conn.commit()

        all_cafe_by_conditions = self.cursor.execute("""SELECT * FROM cafe WHERE name LIKE ? AND location LIKE ? ORDER BY id ASC;""", ("%"+name+"%","%"+location+"%")).fetchall()
        

        self.disconnect_db()

        return all_cafe_by_conditions


db_obj = DB_Actions()


@app.route("/")
def home():
    db = DB_Actions()
    all_cafes = db.get_all_cafes()
    #input(all_cafes[1])
    return render_template("index.html", cafes = all_cafes[1:7])
    

@app.route('/add_new_cafe', methods=["GET", "POST"])
def add_new_cafe():
    add_cafe_form = AddCafeForm()
    db_obj = DB_Actions()

    if(add_cafe_form.validate_on_submit()):
        d = {'name': add_cafe_form.name.data, 'map_url': add_cafe_form.map_url.data, 'img_url': add_cafe_form.img_url.data, 'location': add_cafe_form.location.data, 'has_sockets': add_cafe_form.has_sockets.data,'has_toilet': add_cafe_form.has_toilet.data,'has_wifi': add_cafe_form.has_wifi.data,'can_take_calls': add_cafe_form.can_take_calls.data, 'seats': str(add_cafe_form.seats.data), 'coffee_price': '£'+str(float(add_cafe_form.coffee_price.data))}
        add_cafe_request = requests.post(url='http://localhost:5000/add', data=d).json()
        #input(add_cafe_request)
        flash('New Cafe Added!')
        return render_template('/cafe_added.html')
    return render_template('add_new_cafe.html', form=add_cafe_form)

@app.route('/random', methods=["GET", "POST"])
def get_random():
    get_random_cafe = db_obj.get_random_cafe()
    
    return jsonify(
        cafe={
                    "can_take_calls":get_random_cafe[8],
                    "coffee_price":get_random_cafe[10],
                    "has_socket":get_random_cafe[5],
                    "has_toillet":get_random_cafe[6],
                    "has_wifi":get_random_cafe[7],
                    "id":get_random_cafe[0],
                    "img_url":get_random_cafe[3],
                    "location":get_random_cafe[4],
                    "map_url":get_random_cafe[2],
                    "name":get_random_cafe[1],
                    "seats":get_random_cafe[9]
        }
        )
            

@app.route('/all', methods=["GET", "POST"])
def get_all():
    all_cafe = db_obj.get_all_cafes()
    final_json = []
    for cafe in all_cafe:
            cafe={
                "can_take_calls":cafe[8],
                "coffee_price":cafe[10],
                "has_socket":cafe[5],
                "has_toillet":cafe[6],
                "has_wifi":cafe[7],
                "id":cafe[0],
                "img_url":cafe[3],
                "location":cafe[4],
                "map_url":cafe[2],
                "name":cafe[1],
                "seats":cafe[9]
                }
                
        
            final_json.append(cafe)


    return jsonify(final_json)



@app.route('/search_for_cafe', methods=["GET", "POST"])
def search_for_cafe():
    db_obj = DB_Actions()
    search_cafe_form = SearchForCafeForm()
    if(search_cafe_form.validate_on_submit()):
        cafe_found = db_obj.get_cafe_by_conditions(search_cafe_form.name.data,search_cafe_form.location.data)
        #input(cafe_found)
        return render_template('/cafe_found.html', cafes=cafe_found)
    return render_template('search_for_cafe.html', form=search_cafe_form)


@app.route('/search', methods=["GET", "POST"])
def search_by_location():
    query_location = request.args.get("loc")
    cafes = db_obj.get_cafe_by_location(query_location)
    if(len(cafes) > 0 ):
        final_json = []
        for cafe in cafes:
                cafe={
                    "can_take_calls":cafe[8],
                    "coffee_price":cafe[10],
                    "has_socket":cafe[5],
                    "has_toillet":cafe[6],
                    "has_wifi":cafe[7],
                    "id":cafe[0],
                    "img_url":cafe[3],
                    "location":cafe[4],
                    "map_url":cafe[2],
                    "name":cafe[1],
                    "seats":cafe[9]
                    }
                    
            
                final_json.append(cafe)


        return jsonify(final_json)     
    
    else:
        return jsonify(error={
            "Not Found": "Sorry, we don't have a cafe at that location."
        }),status.HTTP_404_NOT_FOUND


@app.route('/delete_cafe/<int:cafe_id>', methods=["DELETE", "POST", "GET"])
def cafe_delete(cafe_id):
    id = cafe_id
    delete_cafe_request = requests.delete(url='http://localhost:5000/delete/'+str(id)).json()
    return redirect('/')


@app.route('/delete/<int:cafe_id>', methods=["DELETE","GET", "POST"])
def delete(cafe_id):
    id = cafe_id

    try:
        db_obj.delete_cafe(id)
        return jsonify(response={
                "success": "Successfully delete the Cafe."
            })
    
    except:
        return jsonify(error={
                "Not Found": "Sorry a cafe with that id was not found in the database."
            }),status.HTTP_404_NOT_FOUND

@app.route('/add', methods=["POST"])
def add_new():
    name = request.form["name"]
    map_url = request.form["map_url"]
    img_url = request.form["img_url"]
    location = request.form["location"]
    has_sockets = request.form["has_sockets"]
    has_toilet = request.form["has_toilet"]
    has_wifi = request.form["has_wifi"]
    can_take_calls = request.form["can_take_calls"]
    seats = request.form["seats"]
    coffee_price = request.form["coffee_price"]

    db_obj.insert_new_cafe(name,map_url,img_url,location,has_sockets,has_toilet,has_wifi,can_take_calls,seats,coffee_price)

    return jsonify(response={
            "success": "Successfully added the new cafe."
        })




@app.route('/update-price/<int:cafe_id>', methods=["PATCH"])
def update_price(cafe_id):
    id = cafe_id
    coffee_price = request.form["new_price"]
    #input(coffee_price)
    cafe_by_id = db_obj.get_cafe_by_id(id)

    if(len(cafe_by_id) > 0):
        db_obj.update_price(id,coffee_price)

        return jsonify(response={
                "success": "Successfully updated the price."
            })
    
    else:
        return jsonify(error={
                "Not Found": "Sorry a cafe with that id was not found in the database."
            }),status.HTTP_404_NOT_FOUND
    

@app.route('/report-closed/<int:cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    id = int(cafe_id)
    api_key = request.args.get("api-key")
    #input(coffee_price)

    cafe_by_id = db_obj.get_cafe_by_id(id)
    if api_key == "TopSecretAPIKey":
        if(len(cafe_by_id) > 0):
            db_obj.delete_cafe(id)

            return jsonify(response={
                    "success": "Successfully deleted the cafe."
                })
        
        else:
            return jsonify(error={
                    "Not Found": "Sorry a cafe with that id was not found in the database.",
                }),status.HTTP_404_NOT_FOUND
    
    else:
        return jsonify(error={
                "Not Found": "Sorry, that's not allowed. Make sure you have the correct api_key."
            }),status.HTTP_403_FORBIDDEN



# @app.route('/search/<string:loc>', methods=["GET", "POST"])
# def search_by_location(loc):
#     cafes = db_obj.get_cafe_by_location(loc)
    
#     if(len(cafes) > 0 ):
#         final_json = []
#         for cafe in cafes:
#                 cafe={
#                     "can_take_calls":cafe[8],
#                     "coffee_price":cafe[10],
#                     "has_socket":cafe[5],
#                     "has_toillet":cafe[6],
#                     "has_wifi":cafe[7],
#                     "id":cafe[0],
#                     "img_url":cafe[3],
#                     "location":cafe[4],
#                     "map_url":cafe[2],
#                     "name":cafe[1],
#                     "seats":cafe[9]
#                     }
                    
            
#                 final_json.append(cafe)


#         return jsonify(final_json)     
    
#     else:
#         return jsonify(error={
#             "Not Found": "Sorry, we don't have a cafe at that location."
#         })



## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    db_obj.mountTables()
    app.run(debug=True)
