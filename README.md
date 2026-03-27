# Bookstore (Django)

## 1) What does this project do?
An online bookstore with these core features:
- Product management (`bookshop`)
- User accounts and authentication (`users`, `authentication`)
- Shopping cart and coupons (`cart`, `coupons`)
- Orders and payments (`orders`, `payment`)

## 2) Main technologies
- Django
- MySQL
- Docker Compose (Nginx + Django + MySQL)
- Payment integrations: Braintree, VNPay

## 3) Environment setup
Copy the environment template:

```bash
cp bookstore/.env.example bookstore/.env
```

Update key variables in `bookstore/.env`:
- `SECRET_KEY`
- `DB_*`
- `EMAIL_*`
- `BRAINTREE_*`
- `VNPAY_*`

## 4) Quick start with Docker
From the project root:

```bash
docker compose up --build
```

Services:
- Nginx is exposed at `http://localhost`
- Django runs internally on port `8001` in the container
- MySQL runs in the `db` service

## 5) Common commands
Run migrations:

```bash
docker compose exec django_app python manage.py migrate
```

Create an admin user:

```bash
docker compose exec django_app python manage.py createsuperuser
```

Collect static files:

```bash
docker compose exec django_app python manage.py collectstatic --noinput
```

## 6) Main URLs
- Admin: `/admin/`
- Cart: `/cart/`
- Orders: `/orders/`
- Payment: `/payment/`

## 7) Notes
- Payment testing guide: `bookstore/Testing payment .txt`
- If you run locally without Docker, install MySQL and dependencies from `bookstore/requirements.txt`.
