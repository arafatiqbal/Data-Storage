import time
import psycopg2
import argparse
import re
import csv

DBname = "postgres"
DBuser = "postgres"
DBpwd = "1234"
TableName = 'CensusData'
Datafile = "Oregon2015.csv"
CreateDB = False

def row2vals(row):
    for key in row:
        if not row[key]:
            row[key] = 0
        row['County'] = row['County'].replace('\'','')

    ret = f"""
       {row['CensusTract']},            -- CensusTract
       '{row['State']}',                -- State
       '{row['County']}',               -- County
       {row['TotalPop']},               -- TotalPop
       {row['Men']},                    -- Men
       {row['Women']},                  -- Women
       {row['Hispanic']},               -- Hispanic
       {row['White']},                  -- White
       {row['Black']},                  -- Black
       {row['Native']},                 -- Native
       {row['Asian']},                  -- Asian
       {row['Pacific']},                -- Pacific
       {row['Citizen']},                -- Citizen
       {row['Income']},                 -- Income
       {row['IncomeErr']},              -- IncomeErr
       {row['IncomePerCap']},           -- IncomePerCap
       {row['IncomePerCapErr']},        -- IncomePerCapErr
       {row['Poverty']},                -- Poverty
       {row['ChildPoverty']},           -- ChildPoverty
       {row['Professional']},           -- Professional
       {row['Service']},                -- Service
       {row['Office']},                 -- Office
       {row['Construction']},           -- Construction
       {row['Production']},             -- Production
       {row['Drive']},                  -- Drive
       {row['Carpool']},                -- Carpool
       {row['Transit']},                -- Transit
       {row['Walk']},                   -- Walk
       {row['OtherTransp']},            -- OtherTransp
       {row['WorkAtHome']},             -- WorkAtHome
       {row['MeanCommute']},            -- MeanCommute
       {row['Employed']},               -- Employed
       {row['PrivateWork']},            -- PrivateWork
       {row['PublicWork']},             -- PublicWork
       {row['SelfEmployed']},           -- SelfEmployed
       {row['FamilyWork']},             -- FamilyWork
       {row['Unemployment']}            -- Unemployment
    """

    return ret


def initialize():
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--datafile", required=True)
  parser.add_argument("-c", "--createtable", action="store_true")
  args = parser.parse_args()

  global Datafile
  Datafile = args.datafile
  global CreateDB
  CreateDB = args.createtable

def readdata(fname):
    print(f"readdata: reading from File: {fname}")
    with open(fname, mode="r") as fil:
        dr = csv.DictReader(fil)

        rowlist = []
        for row in dr:
            rowlist.append(row)

    return rowlist

def getSQLcmnds(rowlist):
    cmdlist = []
    for row in rowlist:
        valstr = row2vals(row)
        cmd = f"INSERT INTO {TableName} VALUES ({valstr});"
        cmdlist.append(cmd)
    return cmdlist

def dbconnect():
    connection = psycopg2.connect(
            host="localhost",
            database=DBname,
            user=DBuser,
            password=DBpwd,
            )
    connection.autocommit = False
    return connection


def createTable(conn):

    with conn.cursor() as cursor:
        cursor.execute(f"""
            DROP TABLE IF EXISTS {TableName};
            CREATE TABLE {TableName} (
                CensusTract         NUMERIC,
                State               TEXT,
                County              TEXT,
                TotalPop            INTEGER,
                Men                 INTEGER,
                Women               INTEGER,
                Hispanic            DECIMAL,
                White               DECIMAL,
                Black               DECIMAL,
                Native              DECIMAL,
                Asian               DECIMAL,
                Pacific             DECIMAL,
                Citizen             DECIMAL,
                Income              DECIMAL,
                IncomeErr           DECIMAL,
                IncomePerCap        DECIMAL,
                IncomePerCapErr     DECIMAL,
                Poverty             DECIMAL,
                ChildPoverty        DECIMAL,
                Professional        DECIMAL,
                Service             DECIMAL,
                Office              DECIMAL,
                Construction        DECIMAL,
                Production          DECIMAL,
                Drive               DECIMAL,
                Carpool             DECIMAL,
                Transit             DECIMAL,
                Walk                DECIMAL,
                OtherTransp         DECIMAL,
                WorkAtHome          DECIMAL,
                MeanCommute         DECIMAL,
                Employed            INTEGER,
                PrivateWork         DECIMAL,
                PublicWork          DECIMAL,
                SelfEmployed        DECIMAL,
                FamilyWork          DECIMAL,
                Unemployment        DECIMAL
            );
            ALTER TABLE {TableName} ADD PRIMARY KEY (CensusTract);
            CREATE INDEX idx_{TableName}_State ON {TableName}(State);
            """)

        print(f"Created {TableName}")

def load(conn, icmdlist):

    with conn.cursor() as cursor:
        print(f"Loading {len(icmdlist)} rows")
        start = time.perf_counter()

        with open(Datafile) as f:
            cursor.copy_from(f,"censusdata",sep=',')

        elapsed = time.perf_counter() - start
        print(f'Finished Loading. Elapsed Time: {elapsed:0.4} seconds')


def main():
    initialize()
    conn = dbconnect()
    rlis = readdata(Datafile)
    cmdlist = getSQLcmnds(rlis)

    if CreateDB:
        createTable(conn)
    load(conn, cmdlist)

if __name__ == "__main__":
    main()
