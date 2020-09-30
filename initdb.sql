--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3 (Debian 12.3-1.pgdg100+1)
-- Dumped by pg_dump version 12.3 (Debian 12.3-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: artists; Type: TABLE; Schema: public; Owner: play_backend_user
--

CREATE TABLE public.users (
    user_id serial primary key,
    username character varying(255) unique,
    hashed_password character varying(255)
);


ALTER TABLE public.users OWNER TO anna_test_user;

CREATE TABLE public.status (
    status_id serial primary key,
    status_name character varying(20) unique
);

ALTER TABLE public.status OWNER TO anna_test_user;


CREATE TABLE public.tasks (
    task_id serial primary key,
    task_name character varying(255) unique,
    task_description character varying(255),
    task_created timestamp,
    task_status integer,
    task_finish timestamp,
    user_id integer
);

ALTER TABLE public.tasks OWNER TO anna_test_user;

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT task_status_fkey FOREIGN KEY (task_status) REFERENCES public.status(status_id);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT task_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);

insert into public.status (status_name)
values
('Новая'),
('Запланированная'),
('В Работе'),
('Завершённая');

insert into public.users (username, hashed_password)
values ('test_user', 'secret_password');

insert into public.tasks (task_name, task_description, task_created, task_finish, task_status, user_id)
values ('Сделать тестовое', 'Тестовое на fastapi', '2020-09-30 21:00', '2020-10-03 21:00',1, 1);

insert into public.tasks (task_name, task_description, task_created, task_finish, task_status, user_id)
values ('Сделать тестовое2', 'Тестовое на fastapi', '2021-09-30 21:00', '2020-10-03 21:00',1, 1);
