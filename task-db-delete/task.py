#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import logging
from datetime import datetime, timedelta

import sqlalchemy as sa


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


CREATE_STEP = 1000
NUM_STEPS = 50


def main():
    engine = sa.create_engine(
        'postgresql+psycopg2://dev:dev@localhost/alar_studios_testtask_delete',
        echo=True,
    )

    metadata = sa.MetaData()

    big_data = sa.Table(
        'data', metadata,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('timestamp', sa.DateTime),
    )

    logger.info('Create table')
    metadata.create_all(engine)

    conn = engine.connect()

    if not conn.execute(big_data.count()).fetchone()[0]:
        logger.info('Starting create test data...')
        now = datetime.utcnow()

        for s in xrange(NUM_STEPS):
            current_num = (s - 1) * CREATE_STEP
            conn.execute(big_data.insert(), [
                {'timestamp': now - timedelta(minutes=current_num + i)}
                for i in xrange(CREATE_STEP)
            ])

        logger.info('%d records was created' % (
            conn.execute(big_data.count()).fetchone()[0]))

    logger.info('Clean data')
    # select id from data where timestamp <= NOW() - INTERVAL '5 days'
    # AND timestamp >= NOW() - INTERVAL '10 days' limit 100;
    # conn.execute(big_data.delete())


if __name__ == '__main__':
    main()
