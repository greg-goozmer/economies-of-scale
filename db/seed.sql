INSERT INTO users (user_id, user_name) VALUES
    (101, 'student'),
    (102, 'user_102'),
    (103, 'user_103'),
    (104, 'user_104'),
    (105, 'user_105')
ON CONFLICT DO NOTHING;

INSERT INTO expense_items (
    expense_id,
    expense_name,
    expense_description,
    expense_status,
    expense_image_url,
    expense_video_url,
    expense_behavior,
    expense_code,
    expense_creator_id,
    expense_formed_at
) VALUES
    (1, 'Аренда кофемашины',
     'Аренда производственного оборудования относится к постоянным издержкам: платёж не зависит от количества приготовленных напитков в пределах выбранного периода.',
     'published', 'http://localhost:9000/expense-items/coffee_machine_rental.png', 'http://localhost:9000/expense-items/coffee_machine_rental.mp4', 'fixed', 25, 101, now()),
    (2, 'Подписка для кассы',
     'Подписка обеспечивает работу кассового программного обеспечения. Регулярный платёж считается постоянной издержкой и относится к счёту 26.',
     'published', 'http://localhost:9000/expense-items/cash_register_subscription.png', 'http://localhost:9000/expense-items/cash_register_subscription.mp4', 'fixed', 26, 102, now()),
    (3, 'Кофейное зерно',
     'Кофейное зерно непосредственно расходуется при приготовлении напитков, поэтому относится к переменным издержкам и учитывается на счёте 20.',
     'published', 'http://localhost:9000/expense-items/coffee_beans.png', 'http://localhost:9000/expense-items/coffee_beans.mp4', 'variable', 20, 103, now()),
    (4, 'Молоко',
     'Расход молока изменяется вместе с объёмом выпуска молочных напитков, поэтому статья является переменной и относится к счёту 20.',
     'published', 'http://localhost:9000/expense-items/milk.png', 'http://localhost:9000/expense-items/milk.mp4', 'variable', 20, 104, now()),
    (5, 'Бумажные стаканы',
     'Одноразовая упаковка расходуется по мере продажи напитков и образует переменные издержки, учитываемые на счёте 44.',
     'published', 'http://localhost:9000/expense-items/paper_cups.png', 'http://localhost:9000/expense-items/paper_cups.mp4', 'variable', 44, 105, now()),
    (6, 'Крышки для стаканов',
     'Крышки используются вместе со стаканами, поэтому их расход растёт с количеством продаж. Это переменная издержка счёта 44.',
     'published', NULL, NULL, 'variable', 44, 102, now()),
    (7, 'Порционный сахар',
     NULL, 'draft', 'http://localhost:9000/expense-items/sugar_sticks.png', 'http://localhost:9000/expense-items/sugar_sticks.mp4', NULL, NULL, 101, NULL),
    (8, 'Техническое обслуживание',
     'Удалённая статья остаётся в базе и не показывается на страницах приложения.',
     'deleted', NULL, NULL, 'fixed', 25, 101, now())
ON CONFLICT DO NOTHING;

INSERT INTO expense_likes (expense_like_id, user_id, expense_id) VALUES
    (1, 101, 1), (2, 102, 1), (3, 103, 1),
    (4, 101, 2),
    (5, 101, 3), (6, 102, 3), (7, 104, 3), (8, 105, 3),
    (9, 102, 4), (10, 103, 4),
    (11, 104, 5),
    (12, 101, 6), (13, 105, 6)
ON CONFLICT DO NOTHING;

SELECT setval('users_user_id_seq', (SELECT max(user_id) FROM users));
SELECT setval('expense_items_expense_id_seq', (SELECT max(expense_id) FROM expense_items));
SELECT setval('expense_likes_expense_like_id_seq', (SELECT max(expense_like_id) FROM expense_likes));
