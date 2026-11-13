MIN_LEN = 1
MAX_LEN_FIRST_NAME = 128
MAX_LEN_SURNAME = 256
MAX_LEN_USERNAME = 128
TABLE_NAME = "users"
TABLE_SQL_CREATE = """
CREATE TABLE IF NOT EXISTS public.users
(
    uid uuid NOT NULL,
    first_name character varying(150) NOT NULL,
    surname character varying(250) NOT NULL,
    username character varying(250) NOT NULL UNIQUE,
    email character varying(250) NOT NULL UNIQUE,
    hashed_password text NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    modified_at timestamp with time zone NOT NULL,
    PRIMARY KEY (uid)
);

ALTER TABLE IF EXISTS public.users
    OWNER to fastapiuser;
"""
