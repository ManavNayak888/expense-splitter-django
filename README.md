# 💸 Expense Splitter

A Django web application to split expenses among groups of people. Track who paid, calculate balances, and settle debts easily.

---

## Features

- **User Authentication** — Register, login, and logout securely
- **Group Management** — Create groups, add/remove members, delete or leave groups
- **Expense Tracking** — Add, edit, and delete expenses with correct payer selection
- **Equal Split Calculation** — Automatically splits expenses among all group members
- **Balance Summary** — See who owes what in real time
- **Settlement Suggestions** — Get suggestions on who should pay whom to settle all debts
- **Settle Up** — Record actual payments to clear debts
- **Settlement History** — View all past settlements in a group

---

## Tech Stack

- **Backend** — Python, Django
- **Frontend** — Django Templates, Bootstrap 5, Bootstrap Icons
- **Database** — SQLite (development)

---

## Installation

**1. Clone the repository:**
```bash
git clone https://github.com/ManavNayak888/expense-splitter-django.git
cd expense-splitter-django
```

**2. Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root:**
```
SECRET_KEY=your_secret_key_here
DEBUG=True
```

**5. Run migrations:**
```bash
python manage.py migrate
```

**6. Create a superuser (optional):**
```bash
python manage.py createsuperuser
```

**7. Run the development server:**
```bash
python manage.py runserver
```

**8. Open in browser:**
```
http://127.0.0.1:8000/
```

---

## Project Structure

```
expense-splitter-django/
├── core/                   # Project settings and root URLs
├── expenses/               # Main app — groups, expenses, settlements
│   ├── models.py           # Group, Expense, Settlement models
│   ├── views.py            # All views
│   ├── forms.py            # GroupForm, ExpenseForm, AddMemberForm
│   ├── urls.py             # App URLs
│   └── templates/
│       └── expenses/       # All HTML templates
├── users/                  # Authentication app
│   ├── views.py            # Register, login, logout
│   ├── urls.py             # Auth URLs
│   └── templates/
│       └── users/          # Login and register templates
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Usage

1. **Register** an account or login
2. **Create a group** (e.g. "Goa Trip", "Flat Expenses")
3. **Add members** by their username
4. **Add expenses** — select who actually paid
5. **Check balances** — see who owes what
6. **Settle up** — record payments to clear debts
7. **View settlement history** — track all past payments

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, `False` for production |

---

## License

This project is for personal and educational use.
