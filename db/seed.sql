INSERT INTO users (user_id, user_name, user_password_hash) VALUES
    (101, 'student', '!'),
    (102, 'user_102', '!'),
    (103, 'user_103', '!'),
    (104, 'user_104', '!'),
    (105, 'user_105', '!')
ON CONFLICT DO NOTHING;

INSERT INTO costs (
    cost_id,
    cost_name,
    cost_description,
    cost_status,
    cost_image_url,
    cost_video_url,
    cost_behavior,
    cost_code,
    cost_creator_id,
    cost_formed_at
) VALUES
    (1, 'Аренда кофемашины',
     'Аренда производственного оборудования относится к постоянным издержкам: платёж не зависит от количества приготовленных напитков в пределах выбранного периода.',
     'published', 'http://localhost:9000/costs/coffee_machine_rental.png', 'http://localhost:9000/costs/coffee_machine_rental.mp4', 'fixed', 25, 101, now()),
    (2, 'Подписка для кассы',
     'Подписка обеспечивает работу кассового программного обеспечения. Регулярный платёж считается постоянной издержкой и относится к счёту 26.',
     'published', 'http://localhost:9000/costs/cash_register_subscription.png', 'http://localhost:9000/costs/cash_register_subscription.mp4', 'fixed', 26, 102, now()),
    (3, 'Кофейное зерно',
     'Кофейное зерно непосредственно расходуется при приготовлении напитков, поэтому относится к переменным издержкам и учитывается на счёте 20.',
     'published', 'http://localhost:9000/costs/coffee_beans.png', 'http://localhost:9000/costs/coffee_beans.mp4', 'variable', 20, 103, now()),
    (4, 'Молоко',
     'Расход молока изменяется вместе с объёмом выпуска молочных напитков, поэтому статья является переменной и относится к счёту 20.',
     'published', 'http://localhost:9000/costs/milk.png', 'http://localhost:9000/costs/milk.mp4', 'variable', 20, 104, now()),
    (5, 'Бумажные стаканы',
     'Одноразовая упаковка расходуется по мере продажи напитков и образует переменные издержки, учитываемые на счёте 44.',
     'published', 'http://localhost:9000/costs/paper_cups.png', 'http://localhost:9000/costs/paper_cups.mp4', 'variable', 44, 105, now()),
    (6, 'Крышки для стаканов',
     'Крышки используются вместе со стаканами, поэтому их расход растёт с количеством продаж. Это переменная издержка счёта 44.',
     'published', 'http://localhost:9000/costs/missing-image.png', 'http://localhost:9000/costs/missing-video.mp4', 'variable', 44, 102, now()),
    (7, 'Порционный сахар',
     NULL, 'draft', 'http://localhost:9000/costs/sugar_sticks.png', 'http://localhost:9000/costs/sugar_sticks.mp4', NULL, NULL, 101, NULL),
    (8, 'Техническое обслуживание',
     'Удалённая статья остаётся в базе и не показывается на страницах приложения.',
     'deleted', 'http://localhost:9000/costs/missing-image.png', 'http://localhost:9000/costs/missing-video.mp4', 'fixed', 25, 101, now())
ON CONFLICT DO NOTHING;

INSERT INTO cost_likes (cost_like_id, user_id, cost_id) VALUES
    (1, 101, 1), (2, 102, 1), (3, 103, 1),
    (4, 101, 2),
    (5, 101, 3), (6, 102, 3), (7, 104, 3), (8, 105, 3),
    (9, 102, 4), (10, 103, 4),
    (11, 104, 5),
    (12, 101, 6), (13, 105, 6)
ON CONFLICT DO NOTHING;

SELECT setval('users_user_id_seq', (SELECT max(user_id) FROM users));
SELECT setval('costs_cost_id_seq', (SELECT max(cost_id) FROM costs));
SELECT setval('cost_likes_cost_like_id_seq', (SELECT max(cost_like_id) FROM cost_likes));
