# -*- coding: utf-8 -*-

from learn_sqlalchemy import api


def test():
    _ = api


if __name__ == "__main__":
    from learn_sqlalchemy.tests import run_cov_test

    run_cov_test(__file__, "learn_sqlalchemy.api", preview=False)
