#!/bin/bash
# -*- coding: utf-8 -*-

# host = localhost
# port = 43348
# database = postgres
# username = postgres
# password = password
docker run --rm --name learn-sqlalchemy-test-psql-db -p 43348:5432 -e POSTGRES_PASSWORD=password -d postgres:10.6-alpine
sleep 1
