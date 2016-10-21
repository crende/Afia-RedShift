# Afia RedShift POC Ignite

> Big Data is anything which is crash Excel -- @DEVOPS_BORAT

## Schedule
* Day 1:
  * Capturing high-level requirements
  * discussiong RedShift Ecosystem
  * POC demonstration
* Day 2:
  * Deployment walkthrough
  * Analyze and ingest sample data sets
  * Planning for the future

### What RedShift is

#### OLAP
RedShift is built as an On-line Analytical Processing data warehouse.

What are some things to consider when utilizing an OLAP database?
* A relatively low volume of transactions slower query and load times data
* integrity is given lower priority, OLTP and other sources expected to maintain integ.
* intended for long-running periodic queries: complex / multi-dimensionals large
* number of joins aggregation in general ideal for ETL procedures

### What RedShift is not 

#### OLTP

RedShift is _not_ and On-line Transaction Processing database

* do not use Redshift if you expect a high volume of transactions 
* do not useRedshift for ad-hoc transactions 
* do not use Redshift as storage if data integrity is a high priority

### RedShift Limitations and Constaints

There are a lot of things normal Postges (now in 9.3.x) can do that RedShift
(now on 8.0.2) cannot.  Rather than list everything here I've included links to
the relevant documentation
* [Unsupported PostgreSQL Funtions](http://docs.aws.amazon.com/redshift/latest/dg/c_unsupported-postgresql-functions.html)
* [Unsupported PostgreSQL Data Types](http://docs.aws.amazon.com/redshift/latest/dg/c_unsupported-postgresql-datatypes.html)
* [Unsupported PostgreSQL Features](http://docs.aws.amazon.com/redshift/latest/dg/c_unsupported-postgresql-features.html)
* RedShift can only read CSV files from S3 and tables from DynamoDB, files need
* to be in one format or the other before loading.  You cannot load JSON files directly
into RedShift, and OLTP datasources need to be first extracted as CSV to import.
* PK's and FK'S are _informational only_ they aren't enforced or used by RedShift.

#### Other General Limitations
* all CSV files _must_ have a header row.  If there is not a header included the
  the table must be created manually.
* all CSV headers _must_ be lowercase.  Uppercase is interpreted as a keyword. 
*If a header leads with a numeric character it must be quoted.  This isn't
'clean' and should be avoided.  Sometimes this is tricky with datetime columnar
objects nonetheless an alternative naming scheme should be decided upon.
* every single column _must_ have a header associated with it.

### Why all these Constraints? I long for freedom.
Most of these limitations and constraints come from the fact the RedShift is heavily re-tooled to be a
strictly MPP (Massively Parallel Processing) architecture.  Essentially we are
making a trade--by reducing functionality and data type support we're able to
take advantage of RedShifts ability to operate on *extremely large scales*.

### What running on MPP means for indexing
remember that RedShift is a cluster. There is a master node and slices (other nodes) that the data is distributed
between.  This means that instead of working with PK's and FK's we're going to
be working with __SORT KEYS__ and __DIST KEYS__.  Our distribution method is how
data is stored across our cluster, and our sorting method enables us to optimize
for our query methods.

* [Choosing a Data Distribution Style](http://docs.aws.amazon.com/redshift/latest/dg/t_Distributing_data.html)
* [Choosing Sort Keys](http://docs.aws.amazon.com/redshift/latest/dg/t_Sorting_data.html)

at a glance, Compound sort keys will have an effect where queries use lots of
JOINS, GROUP BY, ORDER BY, PARTITION BY, etc.  Interleaving sort keys are ideal
for selective queries utilizing WHERE and on queries using restrictive
predicates on secondary columns.

it should be noted that regardless of what sort type you go with, performance is
going to gradually deteroirate.  Data added to an existing table causes the
'unsorted' region of that table to grow.  Run VACUUM REINDEX and ANALYZE after
large loads to optimize the data for querying.
