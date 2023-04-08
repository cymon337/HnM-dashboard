from flask import Flask, jsonify, request, make_response
from flask_httpauth import HTTPTokenAuth
from flask_restx import Api, Resource, fields
import pymysql
import pymysql.cursors

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
api = Api(app, version='1.0', title='H&M Data API by Sophie Schaesberg', description='A REST API built using FLASK and FLASK-RESTX libraries to request and receive data from a MySQL database', doc='/api/swagger')

API_KEY = "cool-key"

@auth.verify_token
def verify_token(token):
    return token == API_KEY

db_host = 'NotMyRealHost23'
db_user = 'NotMyRealUsername23'
db_pass = 'NotMyRealPassword23'
db_name = 'NotMyRealDBName23'
db_port = 3306

def get_db_connection():
    return pymysql.connect(host=db_host,
                           user=db_user,
                           password=db_pass,
                           db=db_name,
                           port=db_port,
                           cursorclass=pymysql.cursors.DictCursor)

# Define namespaces
register_ns = api.namespace('register', description='User registration operations')
auth_ns = api.namespace('authenticate', description='User authentication operations')
customers_ns = api.namespace('customers', description='Data related to Customers KPIs and Charts')
articles_ns = api.namespace('articles', description='Data related to Articles KPIs and Charts')
transactions_ns = api.namespace('transactions', description='Data related to Transactions KPIs and Charts')

# Define models
register_model = register_ns.model('Register', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(description='Email'),
    'password': fields.String(required=True, description='Password'),
})

authenticate_model = auth_ns.model('Authenticate', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
})

# ------------------------------------------------------------------------------------------------------------------------
#                                                       REGISTER
# ------------------------------------------------------------------------------------------------------------------------

@api.route('/api/register')
class Register(Resource):
    @register_ns.expect(register_model)
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email') or None
        password = data.get('password')

        if not username or not password:
            return {"message": "Username and password are required"}, 400

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO user_credentials (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, email, password))
                connection.commit()
                return {"message": "User registered successfully"}, 201
        except pymysql.err.IntegrityError as e:
            return {"message": f"Error: {str(e)}"}, 400
        except Exception as e:
            return {"message": f"Unexpected error: {str(e)}"}, 500
        finally:
            connection.close()

# ------------------------------------------------------------------------------------------------------------------------
#                                                       LOGIN
# ------------------------------------------------------------------------------------------------------------------------

@api.route('/api/authenticate')
class Authenticate(Resource):
    @auth_ns.expect(authenticate_model)
    def post(self):
        try:
            username = request.json.get('username')
            password = request.json.get('password')

            print(f"Received username: {username}, password: {password}")

            if not username or not password:
                return make_response(jsonify({"error": "Missing username or password"}), 400)

            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM user_credentials WHERE username = %s AND password = %s"
                    cursor.execute(sql, (username, password))
                    result = cursor.fetchone()

                    print(f"Query result: {result}")

                    if result:
                        return jsonify({"success": "User authenticated successfully"})
                    else:
                        return make_response(jsonify({"error": "Invalid username or password"}), 401)
            finally:
                connection.close()
        except Exception as e:
            return make_response(jsonify({"error": f"An unexpected error occurred during authentication: {str(e)}"}), 500)

# ------------------------------------------------------------------------------------------------------------------------
#                                                       CUSTOMERS
# ------------------------------------------------------------------------------------------------------------------------

@api.route('/api/customers')
class Customers(Resource):
    @auth.login_required
    def get(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT customer_id, club_member_status, fashion_news_frequency, age FROM customers ORDER BY RAND() LIMIT 200000"
                cursor.execute(sql)
                result = cursor.fetchall()
                return jsonify(result)
        finally:
            connection.close()

# ------------------------------------------------------------------------------------------------------------------------
#                                                       ARTICLES
# ------------------------------------------------------------------------------------------------------------------------

@api.route('/api/articles')
class Articles(Resource):
    @auth.login_required
    def get(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM articles LIMIT 1000"
                cursor.execute(sql)
                result = cursor.fetchall()
                return jsonify(result)
        finally:
            connection.close()

# ------------------------------------------------------------------------------------------------------------------------
#                                                       TRANSACTIONS
# ------------------------------------------------------------------------------------------------------------------------

@api.route('/api/transactions')
class Transactions(Resource):
    @auth.login_required
    def get(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM transactions ORDER BY RAND() LIMIT 1000"
                cursor.execute(sql)
                result = cursor.fetchall()
                return jsonify(result)
        finally:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=8080)