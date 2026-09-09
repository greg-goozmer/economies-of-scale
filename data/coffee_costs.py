from datetime import date
from decimal import Decimal


BASE_CUPS_PER_MONTH = 1000

coffee_costs = [
    {
        "cost_id": 1,
        "cost_name": "Аренда кофемашины",
        "cost_description": (
            "Аренда обеспечивает кофейный уголок автоматической кофемашиной. "
            "Используется платный вариант аренды Dr.coffee F10 стоимостью "
            "9900 ₽/мес.; предложение «бесплатно при покупке кофе» не "
            "учитывается. Учебная норма, база 1000 напитков/мес.: одна "
            "машина, платный вариант аренды."
        ),
        "cost_status": "published",
        "cost_behavior": "fixed",
        "monthly_cost_rub": Decimal("9900.00"),
        "cost_image_url": (
            "http://localhost:9000/coffee-costs/coffee_machine_rental.png"
        ),
        "cost_video_url": (
            "http://localhost:9000/coffee-costs/coffee_machine_rental.mp4"
        ),
        "cost_liked_by": [101, 102, 103],
        "cost_source_url": "https://coffee.rent/",
        "cost_source_checked_on": date(2026, 9, 8),
    },
    {
        "cost_id": 2,
        "cost_name": "Подписка для кассы",
        "cost_description": (
            "Подписка обеспечивает работу программного обеспечения кассы и "
            "не относится к покупке кассового аппарата. Тариф Эвотор «Смарт», "
            "«Лайт» стоит 3990 ₽/год.; это годовая оплата, а не ежемесячный "
            "платёж. Учебная норма, база 1000 напитков/мес.: 3990 / 12 = "
            "332,50 ₽/мес., распределённый расход."
        ),
        "cost_status": "published",
        "cost_behavior": "fixed",
        "monthly_cost_rub": Decimal("332.50"),
        "cost_image_url": (
            "http://localhost:9000/coffee-costs/cash_register_subscription.png"
        ),
        "cost_video_url": (
            "http://localhost:9000/coffee-costs/cash_register_subscription.mp4"
        ),
        "cost_liked_by": [101],
        "cost_source_url": "https://tariff.evotor.ru/",
        "cost_source_checked_on": date(2026, 9, 8),
    },
    {
        "cost_id": 3,
        "cost_name": "Кофейное зерно",
        "cost_description": (
            "Кофейное зерно используется для приготовления напитков. Tasty "
            "Coffee «Бразилия Серрадо», 1000 г стоит 2439 ₽ по показанной "
            "сниженной цене. Учебная норма, база 1000 напитков/мес.: "
            "1000 × 0,016 кг × 2439 ₽/кг = 39 024,00 ₽/мес."
        ),
        "cost_status": "published",
        "cost_behavior": "variable",
        "monthly_cost_rub": Decimal("39024.00"),
        "cost_image_url": "http://localhost:9000/coffee-costs/coffee_beans.png",
        "cost_video_url": "http://localhost:9000/coffee-costs/coffee_beans.mp4",
        "cost_liked_by": [101, 102, 104, 105],
        "cost_source_url": "https://shop.tastycoffee.ru/coffee/brazilia-1kg",
        "cost_source_checked_on": date(2026, 9, 8),
    },
    {
        "cost_id": 4,
        "cost_name": "Молоко",
        "cost_description": (
            "Молоко используется для приготовления молочного кофе. Петмол "
            "для капучино 3,2%, 1 л, арт. 119653 стоит 145 ₽ при минимальном "
            "заказе 12 шт. Учебная норма, база 1000 напитков/мес.: "
            "1000 × 0,2 л × 145 ₽/л = 29 000,00 ₽/мес.; учитывается "
            "потребление 200 л без округления закупки упаковками."
        ),
        "cost_status": "published",
        "cost_behavior": "variable",
        "monthly_cost_rub": Decimal("29000.00"),
        "cost_image_url": "http://localhost:9000/coffee-costs/milk.png",
        "cost_video_url": "http://localhost:9000/coffee-costs/milk.mp4",
        "cost_liked_by": [102, 103],
        "cost_source_url": "https://swlife.ru/119653",
        "cost_source_checked_on": date(2026, 9, 8),
    },
    {
        "cost_id": 5,
        "cost_name": "Бумажные стаканы",
        "cost_description": (
            "Бумажные стаканы используются для продажи напитков навынос. "
            "Чёрный двухслойный стакан 250 мл, 80 мм, арт. 2241 стоит "
            "6,89 ₽/шт. по сниженной цене; в упаковке 20 шт. Учебная норма, "
            "база 1000 напитков/мес.: 1000 × 6,89 ₽ = 6 890,00 ₽/мес."
        ),
        "cost_status": "published",
        "cost_behavior": "variable",
        "monthly_cost_rub": Decimal("6890.00"),
        "cost_image_url": "http://localhost:9000/coffee-costs/paper_cups.png",
        "cost_video_url": "http://localhost:9000/coffee-costs/paper_cups.mp4",
        "cost_liked_by": [104],
        "cost_source_url": (
            "https://www.odnorazka.ru/shop/odnorazovaya-posuda/stakany/"
            "bumazhnye-stakany/"
            "stakan-bumazhnyj-chernyj-dvuhslojnyj-250-ml/"
        ),
        "cost_source_checked_on": date(2026, 9, 8),
    },
    {
        "cost_id": 6,
        "cost_name": "Крышки для стаканов",
        "cost_description": (
            "Крышки закрывают стаканы с напитками навынос. Чёрная крышка "
            "80 мм с открытым питейником, арт. 1575 стоит 1,79 ₽/шт.; в "
            "упаковке 100 шт. Учебная норма, база 1000 напитков/мес.: "
            "1000 × 1,79 ₽ = 1 790,00 ₽/мес."
        ),
        "cost_status": "published",
        "cost_behavior": "variable",
        "monthly_cost_rub": Decimal("1790.00"),
        "cost_image_url": "http://localhost:9000/coffee-costs/cup_lids.png",
        "cost_video_url": "http://localhost:9000/coffee-costs/cup_lids.mp4",
        "cost_liked_by": [101, 105],
        "cost_source_url": (
            "https://www.odnorazka.ru/shop/odnorazovaya-posuda/stakany/kryshki/"
        ),
        "cost_source_checked_on": date(2026, 9, 8),
    },
    {
        "cost_id": 7,
        "cost_name": "Порционный сахар",
        "cost_description": (
            "Порционный сахар предлагается к напитку отдельными стиками. "
            "Стик 5 г, арт. 7234 стоит 0,83 ₽ по обычной цене; в упаковке "
            "200 шт. Учебная норма, база 1000 напитков/мес.: один стик на "
            "напиток, 1000 × 0,83 ₽ = 830,00 ₽/мес."
        ),
        "cost_status": "draft",
        "cost_behavior": "variable",
        "monthly_cost_rub": Decimal("830.00"),
        "cost_image_url": "http://localhost:9000/coffee-costs/sugar_sticks.png",
        "cost_video_url": "http://localhost:9000/coffee-costs/sugar_sticks.mp4",
        "cost_liked_by": [],
        "cost_source_url": (
            "https://www.barista-ltd.ru/magazin/"
            "sakhar-portsionnyy-v-stikakh-5-g-200sht-02.html"
        ),
        "cost_source_checked_on": date(2026, 9, 8),
    },
]
