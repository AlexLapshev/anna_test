insert into users (username, hashed_password, user_email, confirmed)
values ('anna_test_user', '$6$rounds=656000$qd6ejNiPCAHXLQ0q$3/kUqu/Xuili5leabQFKCO3Q9wf3fmgcyGxjz/KppBc.79t9lM2mXrzA5h9qspCqYCBy/d4M3cJ1j6MP/Drg91', 'test@m.ru', true);

insert into tasks (task_name, task_description, task_created, task_finish, task_status, user_id)
values ('Сделать тестовое', 'Тестовое на fastapi', '2020-09-30 21:00', '2020-10-03 21:00','новая', 1);

insert into tasks (task_name, task_description, task_created, task_finish, task_status, user_id)
values ('Сделать тестовое2', 'Тестовое на fastapi', '2020-09-30 21:00', '2020-10-03 21:00','в работе', 1);

insert into tasks_audit (task_id, user_id, task_operation, prev_value, date_change)
values (1, 1, 'task_name', 'в работе', '2020-10-03 16:01:27');
