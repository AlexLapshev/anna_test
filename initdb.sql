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

CREATE TABLE public.users (
    user_id serial primary key,
    username character varying(15) unique,
    hashed_password character varying(255)
);


ALTER TABLE public.users OWNER TO anna_test_user;

CREATE TYPE public.status AS ENUM ('новая', 'запланированная', 'в работе', 'завершённая');

ALTER TYPE public.status OWNER TO anna_test_user;


CREATE TABLE public.tasks (
    task_id serial primary key,
    task_name character varying(25),
    task_description character varying(255),
    task_created timestamp,
    task_status public.status,
    task_finish timestamp,
    user_id integer
);


ALTER TABLE public.tasks OWNER TO anna_test_user;


CREATE TABLE public.tasks_audit (
    audit_id serial primary key,
    task_id integer,
    user_id integer,
    task_operation character varying(25),
    prev_value character varying(255),
    date_change timestamp
);

ALTER TABLE ONLY public.tasks_audit
    ADD CONSTRAINT task_id_audit_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(task_id);

ALTER TABLE ONLY public.tasks_audit
    ADD CONSTRAINT user_id_audit_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT task_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);