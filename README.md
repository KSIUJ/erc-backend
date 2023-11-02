# erc-backend

## How to run (development)

1. Install Python3
2. Clone this project
3. Create and activate a virtual environment in the directory of this project (`python3 -m venv .venv && ./.venv/bin/activate`) (optional)
4. Install dependencies `pip3 install -r requirements.txt`
5. Run migrations `python3 manage.py migrate`
6. Start the server `python3 manage.py runserver`

Server should start on `127.0.0.1:8000`.

To login, open `http://127.0.0.1:8000/accounts/login/` in your browser and login with your faculty account.

