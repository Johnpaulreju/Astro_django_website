# Django Project Setup

## 📌 Prerequisites

Make sure you have **Anaconda** installed before proceeding.

---

## 🚀 Setting Up the Project

### 1⃣ Create a Virtual Environment

```sh
conda create -n djangoproject python=3.12
conda activate djangoproject
```

### 2⃣ Install Django

```sh
pip install django
```

### 3⃣ Run Migrations

```sh
python manage.py migrate
```

### 4⃣ Create a Superuser (for Admin Panel)

```sh
python manage.py createsuperuser
```

You will be prompted to enter:

- **Username**
- **Email**
- **Password**

### 5⃣ Apply Migrations for Your App

```sh
python manage.py makemigrations myapp
python manage.py migrate
```

### 6⃣ Run the Django Development Server

```sh
python manage.py runserver
```

---

## 🌐 Accessing the Application

🔹 **Admin Panel:** [https://127.0.0.1:8000/admin](https://127.0.0.1:8000/admin)  
 _(Use the credentials from `createsuperuser`)_

🔹 **Home Page:** [https://127.0.0.1:8000/](https://127.0.0.1:8000/)

---

## 🎯 Notes

- The admin panel allows you to manage database records.
- Use `conda activate djangoproject` whenever working on the project.
- If you face any issues, try restarting the server (`CTRL + C` then `python manage.py runserver`).
