import requests

BASE_URL = 'http://localhost:8000/api/'
USERNAME = 'apitestuser'
PASSWORD = 'apitestpass123'
EMAIL = 'apitestuser@example.com'

def print_response(resp):
    print(f'URL: {resp.request.url}')
    print(f'Status: {resp.status_code}')
    try:
        print('Response:', resp.json())
    except Exception:
        print('Response:', resp.text)
    print('-' * 40)

def register_user():
    resp = requests.post(BASE_URL + 'register/', json={
        'username': USERNAME,
        'password': PASSWORD,
        'email': EMAIL
    })
    print('Register User:')
    print_response(resp)

def login_user():
    resp = requests.post(BASE_URL + 'login/', json={
        'username': USERNAME,
        'password': PASSWORD
    })
    print('Login User:')
    print_response(resp)
    return resp.json().get('access')

def crud_author(token):
    headers = {'Authorization': f'Bearer {token}'}
    # Create
    resp = requests.post(BASE_URL + 'authors/', json={
        'name': 'Jane Austen',
        'birth_date': '1775-12-16',
        'nationality': 'British',
        'biography': 'English novelist known for her six major novels.',
        'email': 'jane.austen@example.com'
    }, headers=headers)
    print('Create Author:')
    print_response(resp)
    author_id = resp.json().get('id')
    # List
    resp = requests.get(BASE_URL + 'authors/', headers=headers)
    print('List Authors:')
    print_response(resp)
    # Update
    resp = requests.patch(BASE_URL + f'authors/{author_id}/', json={'biography': 'Updated bio.'}, headers=headers)
    print('Update Author:')
    print_response(resp)
    # Delete
    resp = requests.delete(BASE_URL + f'authors/{author_id}/', headers=headers)
    print('Delete Author:')
    print_response(resp)
    return author_id

def crud_publisher(token):
    headers = {'Authorization': f'Bearer {token}'}
    # Create
    resp = requests.post(BASE_URL + 'publishers/', json={
        'name': 'Penguin Books',
        'address': '80 Strand, London, WC2R 0RL, England',
        'website': 'https://www.penguin.co.uk',
        'contact_email': 'info@penguin.co.uk',
        'established_year': 1935
    }, headers=headers)
    print('Create Publisher:')
    print_response(resp)
    publisher_id = resp.json().get('id')
    # List
    resp = requests.get(BASE_URL + 'publishers/', headers=headers)
    print('List Publishers:')
    print_response(resp)
    # Update
    resp = requests.patch(BASE_URL + f'publishers/{publisher_id}/', json={'address': 'Updated address.'}, headers=headers)
    print('Update Publisher:')
    print_response(resp)
    # Delete
    resp = requests.delete(BASE_URL + f'publishers/{publisher_id}/', headers=headers)
    print('Delete Publisher:')
    print_response(resp)
    return publisher_id

def crud_book(token, author_id, publisher_id):
    headers = {'Authorization': f'Bearer {token}'}
    # Create
    resp = requests.post(BASE_URL + 'books/', json={
        'title': 'Pride and Prejudice',
        'author': author_id,
        'publisher': publisher_id,
        'publication_date': '1813-01-28',
        'isbn': '9780141439518',
        'summary': 'A romantic novel of manners.'
    }, headers=headers)
    print('Create Book:')
    print_response(resp)
    book_id = resp.json().get('id')
    # List
    resp = requests.get(BASE_URL + 'books/', headers=headers)
    print('List Books:')
    print_response(resp)
    # Update
    resp = requests.patch(BASE_URL + f'books/{book_id}/', json={'summary': 'Updated summary.'}, headers=headers)
    print('Update Book:')
    print_response(resp)
    # Delete
    resp = requests.delete(BASE_URL + f'books/{book_id}/', headers=headers)
    print('Delete Book:')
    print_response(resp)

def main():
    register_user()
    token = login_user()
    if not token:
        print('Login failed, cannot continue tests.')
        return
    author_id = crud_author(token)
    publisher_id = crud_publisher(token)
    crud_book(token, author_id, publisher_id)

if __name__ == '__main__':
    main() 