# orders-django-backend

---

## 🚀 Overview

**Orders Backend** is a robust backend system for a multi-restaurant food ordering platform. It supports restaurant menu management, multi-cart handling, asynchronous processing, caching, and secure online payments.

The system is designed using modern backend best practices including Celery-based async workers, Redis caching, and containerized deployment.

---

## ✨ Key Features

### 🍽️ Multi-Restaurant Ordering
- Browse menus from multiple restaurants
- Add items from different restaurants
- Maintain **separate carts per restaurant**
- Choose which cart to checkout

### 🛍️ Smart Cart System
- Independent cart per restaurant
- Prevents cross-restaurant order conflicts
- Flexible checkout selection

### 💳 Razorpay Integration
- Secure online payment processing
- Seamless order payment flow
- Production-ready payment handling

### ⚡ Asynchronous Processing
Powered by **Celery + Redis**
- Background task execution
- Email/notification handling
- Improved API responsiveness
- Scalable worker architecture

### 🚀 Redis Caching
- High-speed data retrieval
- Reduced database load
- Improved performance

### 🐳 Docker Support
- Containerized services
- Easy local setup
- Production-friendly deployment

---

## 🧱 Tech Stack

- **Backend:** Django / Django REST Framework  
- **Async Tasks:** Celery  
- **Message Broker & Cache:** Redis  
- **Database:** PostgreSQL  
- **Payments:** Razorpay  
- **Containerization:** Docker & Docker Compose  

---

## 🛠️ Local Setup

### Create Virtual Environment

```bash
python -m venv myvenv
```

### Create Virtual Environment
```bash
./myvenv/Scripts/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Running the Server
```bash
python manage.py runserver
```

### Start Celery Worker
```
celery -A orders_backend worker -l info -P solo
```

## 🐳 Docker Setup
```bash
docker compose -f docker/db.yml -f docker/app.yml up -d --build
```
