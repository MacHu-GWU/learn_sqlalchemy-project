#!/bin/bash
# -*- coding: utf-8 -*-

# host = localhost
# port = 38835
# database = postgres
# username = postgres
# password = password
docker run --rm --name learn-sqlalchemy-test-psql-db -p 38835:5432 -e POSTGRES_PASSWORD=password -d postgres:15.7-alpine
sleep 1
