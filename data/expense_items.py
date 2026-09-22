from datetime import date


BASE_OUTPUT_UNITS = 1000

expense_items = [
    {
        "expense_id": 1,
        "expense_name": "Аренда кофемашины",
        "expense_description": (
            "Аренда производственного оборудования относится к постоянным "
            "издержкам: платёж не зависит от количества приготовленных напитков "
            "в пределах выбранного периода. В учебной модели статья учитывается "
            "на счёте 25 «Общепроизводственные расходы»."
        ),
        "expense_status": "published",
        "expense_behavior": "fixed",
        "expense_code": 25,
        "expense_image_url": (
            "http://localhost:9000/expense-items/coffee_machine_rental.png"
        ),
        "expense_video_url": (
            "http://localhost:9000/expense-items/coffee_machine_rental.mp4"
        ),
        "expense_liked_by": [101, 102, 103],
        "expense_source_url": "https://coffee.rent/",
        "expense_source_checked_on": date(2026, 9, 8),
    },
    {
        "expense_id": 2,
        "expense_name": "Подписка для кассы",
        "expense_description": (
            "Подписка обеспечивает работу кассового программного обеспечения. "
            "Регулярный платёж в учебной модели считается постоянной издержкой и "
            "относится к счёту 26 «Общехозяйственные расходы»."
        ),
        "expense_status": "published",
        "expense_behavior": "fixed",
        "expense_code": 26,
        "expense_image_url": (
            "http://localhost:9000/expense-items/cash_register_subscription.png"
        ),
        "expense_video_url": (
            "http://localhost:9000/expense-items/cash_register_subscription.mp4"
        ),
        "expense_liked_by": [101],
        "expense_source_url": "https://tariff.evotor.ru/",
        "expense_source_checked_on": date(2026, 9, 8),
    },
    {
        "expense_id": 3,
        "expense_name": "Кофейное зерно",
        "expense_description": (
            "Кофейное зерно непосредственно расходуется при приготовлении "
            "напитков, поэтому относится к переменным издержкам. В учебной "
            "модели прямые производственные затраты учитываются на счёте 20 "
            "«Основное производство»."
        ),
        "expense_status": "published",
        "expense_behavior": "variable",
        "expense_code": 20,
        "expense_image_url": "http://localhost:9000/expense-items/coffee_beans.png",
        "expense_video_url": "http://localhost:9000/expense-items/coffee_beans.mp4",
        "expense_liked_by": [101, 102, 104, 105],
        "expense_source_url": "https://shop.tastycoffee.ru/coffee/brazilia-1kg",
        "expense_source_checked_on": date(2026, 9, 8),
    },
    {
        "expense_id": 4,
        "expense_name": "Молоко",
        "expense_description": (
            "Расход молока изменяется вместе с объёмом выпуска молочных "
            "напитков, поэтому статья является переменной. В учебной модели "
            "это прямые затраты счёта 20 «Основное производство»."
        ),
        "expense_status": "published",
        "expense_behavior": "variable",
        "expense_code": 20,
        "expense_image_url": "http://localhost:9000/expense-items/milk.png",
        "expense_video_url": "http://localhost:9000/expense-items/milk.mp4",
        "expense_liked_by": [102, 103],
        "expense_source_url": "https://swlife.ru/119653",
        "expense_source_checked_on": date(2026, 9, 8),
    },
    {
        "expense_id": 5,
        "expense_name": "Бумажные стаканы",
        "expense_description": (
            "Одноразовая упаковка расходуется по мере продажи напитков и "
            "образует переменные издержки. В учебной модели статья отнесена к "
            "счёту 44 «Расходы на продажу»."
        ),
        "expense_status": "published",
        "expense_behavior": "variable",
        "expense_code": 44,
        "expense_image_url": "http://localhost:9000/expense-items/paper_cups.png",
        "expense_video_url": "http://localhost:9000/expense-items/paper_cups.mp4",
        "expense_liked_by": [104],
        "expense_source_url": (
            "https://www.odnorazka.ru/shop/odnorazovaya-posuda/stakany/"
            "bumazhnye-stakany/"
            "stakan-bumazhnyj-chernyj-dvuhslojnyj-250-ml/"
        ),
        "expense_source_checked_on": date(2026, 9, 8),
    },
    {
        "expense_id": 6,
        "expense_name": "Крышки для стаканов",
        "expense_description": (
            "Крышки используются вместе с одноразовыми стаканами, поэтому их "
            "расход растёт с количеством продаж. В учебной модели переменная "
            "статья учитывается на счёте 44 «Расходы на продажу»."
        ),
        "expense_status": "published",
        "expense_behavior": "variable",
        "expense_code": 44,
        "expense_image_url": "http://localhost:9000/expense-items/cup_lids.png",
        "expense_video_url": "http://localhost:9000/expense-items/cup_lids.mp4",
        "expense_liked_by": [101, 105],
        "expense_source_url": (
            "https://www.odnorazka.ru/shop/odnorazovaya-posuda/stakany/kryshki/"
        ),
        "expense_source_checked_on": date(2026, 9, 8),
    },
    {
        "expense_id": 7,
        "expense_name": "Порционный сахар",
        "expense_description": (
            "Порционный сахар расходуется вместе с напитками и относится к "
            "переменным издержкам. В учебной модели это прямые затраты счёта 20 "
            "«Основное производство»."
        ),
        "expense_status": "draft",
        "expense_behavior": "variable",
        "expense_code": 20,
        "expense_image_url": "http://localhost:9000/expense-items/sugar_sticks.png",
        "expense_video_url": "http://localhost:9000/expense-items/sugar_sticks.mp4",
        "expense_liked_by": [],
        "expense_source_url": (
            "https://www.barista-ltd.ru/magazin/"
            "sakhar-portsionnyy-v-stikakh-5-g-200sht-02.html"
        ),
        "expense_source_checked_on": date(2026, 9, 8),
    },
]
