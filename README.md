# Library Service API 
Api for Library Service written on DRF. Stripe api, celery, telegram notifications.
Service for borrowing books in library with telegram notifications and stripe payments.


## Features
- JWT Token authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/, /api/doc/redoc/ 
- Create user and profiles, edit and delete your own profile
- Creating and updating Books
- Creating Borrowings, creating payments for borrowings, return borrowings
- Search borrowings by user and active/inactive
- Telegram notification for borrowings creating, overdue borrowings, successful payments
- creating and renew stripe payment session

### Installing using GitHub
Python3 must be already installed. Install PostgresSQL and create db.


```shell
git clone https://github.com/asdadaversa/Library.git
cd library
python3 -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
```

### Telegram Token setup
```
- Open Telegram and search for '@BotFather'.
- Start a chat with '@BotFather'.
- Type '/newbot' to create a new bot.
- Follow the instructions to set a name and username for your bot.
- Once your bot is created, '@BotFather' will provide you with a unique token.

example telegram token
TELEGRAM_TOKEN="6991708756:AAHOjZuNtwSs2hmDuYbpOYy9Xp3LXDVc125"

To get chat id run library_telegram_bot/bot.py and make /start command in telegram bot
CHAT_ID="55192146"

```
### Stipe api key setup
```
- Log in to your Stripe account at stripe.com.
- Go to the 'Developers' or 'API keys' section.
- Click on 'Create a key'.
- Stripe will provide you with two keys: the Secret Key for server-side authentication and the 
Publishable Key for client-side use in your web application.
- 4242424242424242 12/2026 314 stripe test card
```


### Celery setup
```
celery -A library_service worker --loglevel=INFO
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### Environment Variables Setup
1. Create a `.env` file in the root directory of your project.
2. Set up it as in '.env.sample'
```
SECRET_KEY=SECRET_KEY
POSTGRES_HOST=POSTGRES_HOST
POSTGRES_DB=POSTGRES_DB
POSTGRES_USER=POSTGRES_USER
POSTGRES_PASSWORD=POSTGRES_PASSWORD
DB_PORT=DB_PORT
TELEGRAM_TOKEN="6991708756:AAHOjZuNtwSs2hmDuYbpOYy9Xp3LXDVc125"
CHAT_ID="55192999"
SECRET_STRIPE_KEY=sk_test_51PBg0LRu0QmZgMhxbjasgfCPOLONKY7FYFl4lXLykzriNxVtDxzje31PSLi913pmaFELZ0CJmUlDfUFnzwg9ZwP00IUm2K3v4
CELERY_BROKER_URL='redis://localhost/1'
CELERY_RESULT_BACKEND='redis://localhost/2'
```

### Next run migrations and run server

```bash
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver

```


## Use the following command to load prepared data from fixture:

`python manage.py loaddata db_data.json`

- After loading data from fixture you can use following superuser (or create another one by yourself):
  - email: `admin@example.com`
  - Password: `Qwerty.1`



## Run with docker
Docker should be installed
```
set up your .env for docker, for e.g.
POSTGRES_HOST=db
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secretpassword
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

next run:
- docker-compose build
- docker-compose up

create superuser:
docker-compose run app python manage.py createsuperuser

```



## Getting access:
  - Create user - /api/users/
  - Get access token - /api/users/token/

  - You can load ModHeader extension for your browser and add request header token. Example:
  - key: Authorize
  - value:Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1ODA4NzYzLCJpYXQiOjE3MTU3OTA3NjMsImp0aSI6IjdmNThkOWRjODhmNjQwODdhZDdmNGZjNjRlZTBhMTdmIiwidXNlcl9pZCI6Mn0.o0Em-E0y47llU5hUJt57R3dLGvMDIEgvBi0TR8ElouE



## API Endpoints
<details>
  <summary>Users</summary>

- **Create User**: `POST /api/users/`
- **Login**: `POST /api/users/token/`
- **Login**: `POST /api/users/refresh/`
- **Login**: `POST /api/users/verify/`
- **Retrieve User Profile**: `GET /api/user/me/`
- **Put User Profile**: `PUT /api/user/me/`
- **Delete User Profile**: `DELETE /api/user/me/`

</details>


<details>
  <summary>Books</summary>

- **List Books**: `GET /api/books/`
- **Create Books**: `POST /api/books/`
- **Retrieve Book**: `GET /api/books/{book_id}/`
- **Update Book**: `PUT /api/books/{book_id}/`
- **Delete Book**: `DELETE /api/books/{book_id}/`

</details>


<details>
  <summary>Borrowings</summary>

- **List Borrowings**: `GET /api/borrowings/`
- **Create Borrowings**: `POST /api/borrowings/`
- **Retrieve Borrowing**: `GET /api/borrowings/{borrowing_id}/`
- **Borrowing return**: `GET /api/borrowings/{borrowing_id}/return`
</details>

<details>
  <summary>Payments</summary>

- **List Payments**: `GET /api/payments/`
- **Retrieve Payments**: `GET /api/payments/{payment_id}/`
- **Borrowing Return**: `GET /api/borrowings/{borrowing_id}/return/`
- **Borrowing Renew**: `GET /api/borrowings/{borrowing_id}/renew/`
</details>

## Documentation
- The API is documented using the OpenAPI standard.
- Access the API documentation by running the server and navigating to http://127.0.0.1:8000/api/doc/swagger/ or http://127.0.0.1:8000/api/doc/redoc/.

fgdfgdfgdfg
docker-compose run app python manage.py createsuperuser

## Contributing
Feel free to contribute to these enhancements, and let's make our Library Service API even better!
