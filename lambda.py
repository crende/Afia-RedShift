import sqlalchemy, csv, sys, time, re, datetime, pg8000, pytz
from datetime import timedelta
from pytz import timezone
from dateutil.parser import parse
from time import time
from sqlalchemy import create_engine, Column, Integer, Float, String, Table, Date, DateTime, exc, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

class RedShiftLoader(object):

    def __init__(self, event, context):
        self.bucket = event['Records'][0]['s3']['bucket']['name']
        self.key = event['Records'][0]['s3']['object']['key']
        self.file = self.key.split('/')[-1]
        self.table = self.file.split('/')[-1].split('.')[0]
        self.engine = create_engine('postgresql+pg8000://admin:PassyMcPassword1@afia-testing-redshift-1euhr9iz4zhiv.c3wfxedajom1.us-east-1.redshift.amazonaws.com:5439/test', echo=True)
        self.context = context
        self.tp = '^\d{2}:\d{2}:\d{2}$'
        self.dp = '^\d{4}-\d{2}-\d{2}$'
        self.dt = '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        self.h = self.get_headers()[0]
        self.f = self.get_headers()[1]
        self.l = self.csvlist()
        self.Base = declarative_base(self.engine)

    def get_headers(self):
        with open(self.file, newline='') as fp:
            r = csv.reader(fp)
            h = next(r)
            f = next(r)
        return h, f

    def csvlist(self):
        with open(self.file, newline='') as fp:
            r = csv.reader(fp)
            l = list(r)
        l = l[1:]
        for x in l:
            try:
                for y, z in enumerate(x):
                    if re.match(self.dp, z) and isinstance(parse(z).date(), datetime.date):
                        x[y] = parse(z).date()

                    if re.match(self.tp, z) and isinstance(parse(z).time(), datetime.time):
                        x[y] = parse(z)

                    if re.match(self.dt, z) and isinstance(parse(z), datetime.datetime):
                        x[y] = parse(z)

            except ValueError as e:
                print(e)
                pass
        return l

    def istime(self, x):
        if re.match(self.tp, x) and isinstance(parse(x).time(), datetime.time):
            return True

    def isdate(self, x):
            p4print(e)
        if re.match(self.dp, x) and isinstance(parse(x).date(), datetime.date):
            return True

    def isdatetime(self, x):
        if re.match(self.dt, x) and isinstance(parse(x), datetime.datetime):
            return True

    def isfloat(self, x):
        try:
            if isinstance(float(x), float):
                return True
        except ValueError as e:
            print(e)
            return False

    def create_table(self):
        t = Table(self.table, self.Base.metadata, 
            Column('id', Integer, autoincrement=False, nullable=False, primary_key=True),
            *(Column(x[0], String(60), nullable=True) if x[1].isalpha()
                else Column(x[0], Date, nullable=True) if self.isdate(x[1])
                else Column(x[0], DateTime(timezone=False), nullable=True) if self.istime(x[1])
                else Column(x[0], DateTime(timezone=False), nullable=True) if self.isdatetime(x[1])
                else Column(x[0], Integer, nullable=True) if x[1].isdigit()
                else Column(x[0], Float, nullable=True) if self.isfloat(x[1])
                else Column(x[0], String(60), nullable=True)
                for x in zip(self.h, self.f)))

        self.Base.metadata.create_all(self.engine, checkfirst=True)

    def load_table(self):
        self.Base = automap_base()
        self.Base.prepare(engine=self.engine, reflect=True)
        Loader = getattr(self.Base.classes, self.table)

        session = sessionmaker(bind=self.engine)
        s = session()

        try:
            id = 0
            for i in self.l:
                tmp_id = { 'id' : id }
                tmp_id.update(dict(zip(self.h, i)))
                r = Loader(**tmp_id)
                id += 1
                s.add(r)
            s.commit()
        except Exception as e:
            s.rollback()
            print(e)
        finally:
            s.close()

def lambda_handler(event, context):
    t = time()
    redshift_load = RedShiftLoader(event, context)
    redshift_load.create_table()
    redshift_load.load_table()
    print("Time elapsed: " + str(time() - t) + " s.")
