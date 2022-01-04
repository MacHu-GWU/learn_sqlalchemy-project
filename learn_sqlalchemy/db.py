# -*- coding: utf-8 -*-

import sqlalchemy_mate as sam

engine_sqlite = sam.EngineCreator().create_sqlite()
engine_psql = sam.EngineCreator(
    host="localhost",
    port=38835,
    database="postgres",
    username="postgres",
    password="password",
).create_postgresql_pg8000()
