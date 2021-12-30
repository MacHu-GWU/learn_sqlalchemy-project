# -*- coding: utf-8 -*-

import sqlalchemy_mate as sam

engine_sqlite = sam.EngineCreator().create_sqlite()
engine_psql = sam.EngineCreator(
    host="localhost",
    port=43348,
    database="postgres",
    username="postgres",
    password="password",
).create_postgresql_pg8000()
