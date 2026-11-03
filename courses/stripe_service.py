import stripe
from django.conf import settings
from .models import Payment, Course

# Устанавливаем секретный ключ при инициализации модуля
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product_and_price(course: Course, amount_cents: int):
    """
    Создает продукт и цену в Stripe.
    Возвращает price_id.

    :param course: Объект курса из БД
    :param amount_cents: Цена в центах (целое число)
    :return: price_id (строка)
    """
    try:
        # 1. Создаем продукт (название курса)
        product = stripe.Product.create(
            name=course.title,
            description=course.description or "Курс на платформе",
        )

        # 2. Создаем цену (amount в центах, валюта USD для теста)
        price = stripe.Price.create(
            unit_amount=amount_cents,
            currency="usd",  # Для тестов Stripe почти всегда использует USD.
            # Если нужна RUB, убедись, что твой аккаунт поддерживает эту валюту.
            product=product.id,
        )
        return price.id
    except Exception as e:
        print(f"Ошибка создания продукта/цены в Stripe: {e}")
        raise e


def create_checkout_session(user, course: Course, price_id: str, success_url: str, cancel_url: str, amount_cents: int):
    """
    Теперь amount_cents передаем явно, чтобы не гадать в ответе Stripe.
    """
    try:
        session = stripe.CheckoutSession.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )

        # Теперь amount берем из аргумента, а не парсим ответ Stripe
        payment = Payment.objects.create(
            user=user,
            course=course,
            stripe_session_id=session.id,
            amount=amount_cents,  # ✅ Надежно: берем то, что передали
            status='pending'
        )

        return session.id, session.url, payment.id

    except Exception as e:
        print(f"Ошибка создания сессии оплаты: {e}")
        raise e
