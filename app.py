import json
import pyodbc
import os

def get_db_connection():
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={os.environ["DB_HOST"]};'
        f'DATABASE={os.environ["DB_NAME"]};'
        f'UID={os.environ["DB_USER"]};'
        f'PWD={os.environ["DB_PASS"]}'
    )
    return conn

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    if http_method == 'GET' and path == '/users':
        return list_users()
    elif http_method == 'POST' and path == '/users':
        return create_user(json.loads(event['body']))
    elif http_method == 'GET' and path.startswith('/users/'):
        user_id = path.split('/')[-1]
        return get_user(user_id)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Bad Request'})
        }

def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TblUsers")
    rows = cursor.fetchall()
    users = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    conn.close()
    return {
        'statusCode': 200,
        'body': json.dumps(users)
    }

def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TblUsers WHERE Id=?", user_id)
    row = cursor.fetchone()
    conn.close()
    if row:
        user = dict(zip([column[0] for column in cursor.description], row))
        return {
            'statusCode': 200,
            'body': json.dumps(user)
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'User not found'})
        }

def create_user(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO TblUsers (CompanyFacilityId, CompanyId, Email, FirstName, LastName, Phone, Gender, Status, LanguageId, CoachId, StudentId, IsAccountCreated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user['CompanyFacilityId'], user['CompanyId'], user['Email'], user['FirstName'], user['LastName'], user['Phone'], user['Gender'], user['Status'], user['LanguageId'], user['CoachId'], user['StudentId'], user['IsAccountCreated']))
    conn.commit()
    conn.close()
    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'User created successfully'})
    }
