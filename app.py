# Custom extension for IBM Watson Assistant which provides a
# REST API around a single database table (SERVICECOVERAGES).
#
# The code demonstrates how a simple REST API can be developed and
# then deployed as serverless app to IBM Cloud Code Engine.
#
# See the README and related tutorial for details.
#
# Written by Henrik Loeser (data-henrik), hloeser@de.ibm.com
# (C) 2022 by IBM

import os
import ast
import urllib.parse
from dotenv import load_dotenv
from apiflask import APIFlask, Schema, HTTPTokenAuth, PaginationSchema, pagination_builder, abort
from apiflask.fields import Integer, String, Boolean, Date, List, Nested
from apiflask.validators import Length, Range
# Database access using SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Set how this API should be titled and the current version
API_TITLE='Service Coverages API for Watson Assistant'
API_VERSION='1.0.0'

# create the app
app = APIFlask(__name__, title=API_TITLE, version=API_VERSION)

# load .env if present
load_dotenv()

# the secret API key, plus we need a username in that record
API_TOKEN="{{'{0}':'appuser'}}".format(os.getenv('API_TOKEN'))
#convert to dict:
tokens=ast.literal_eval(API_TOKEN)

# database URI
DB2_URI=os.getenv('DB2_URI')
# optional table arguments, e.g., to set another table schema
ENV_TABLE_ARGS=os.getenv('TABLE_ARGS')
TABLE_ARGS=None
if ENV_TABLE_ARGS:
    TABLE_ARGS=ast.literal_eval(ENV_TABLE_ARGS)


# specify a generic SERVERS scheme for OpenAPI to allow both local testing
# and deployment on Code Engine with configuration within Watson Assistant
app.config['SERVERS'] = [
    {
        'description': 'Code Engine deployment',
        'url': 'https://{appname}.{projectid}.{region}.codeengine.appdomain.cloud',
        'variables':
        {
            "appname":
            {
                "default": "myapp",
                "description": "application name"
            },
            "projectid":
            {
                "default": "projectid",
                "description": "the Code Engine project ID"
            },
            "region":
            {
                "default": "us-south",
                "description": "the deployment region, e.g., us-south"
            }
        }
    },
    {
        'description': 'local test',
        'url': 'http://127.0.0.1:{port}',
        'variables':
        {
            'port':
            {
                'default': "5000",
                'description': 'local port to use'
            }
        }
    }
]


# set how we want the authentication API key to be passed
auth=HTTPTokenAuth(scheme='ApiKey', header='API_TOKEN')

# configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI']=DB2_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize SQLAlchemy for our database
db = SQLAlchemy(app)


# sample records to be inserted after table recreation
sample_coverages=[
    {
        "shortname":"Sample",
        "gbg":"Sample",
        "crosstps":"Sample",
        "crosstpsm":"Sample",
        "mgexec":"Sample",
        "mgexecm":"Sample",
        "silablead":"Sample",
        "silableadm":"Sample",
        "solarch":"Sample",
        "solarchm":"Sample",
        "bpsdaa":"Sample",
        "bpsdaam":"Sample",
        "bpssec":"Sample",
        "bpssecm":"Sample",
        "bpssus":"Sample",
        "bpssusm":"Sample",
        "bpsz":"Sample",
        "bpszm":"Sample",
        "bpspow":"Sample",
        "bpspowm":"Sample",
        "bpsstor":"Sample",
        "bpsstorm":"Sample",
        "bpscloud":"Sample",
        "bpscloudm":"Sample",
        "crosspts":"Sample",
        "crossptsm":"Sample",
        "ptsda":"Sample",
        "ptsdam":"Sample",
        "ptsauto":"Sample",
        "ptsautom":"Sample",
        "ptssec":"Sample",
        "ptssecm":"Sample",
        "ptssus":"Sample",
        "ptssusm":"Sample",
        "ptsz":"Sample",
        "ptszm":"Sample",
        "ptspow":"Sample",
        "ptspowm":"Sample",
        "ptsstor":"Sample",
        "ptsstorm":"Sample",
        "ptscloud":"Sample",
        "ptscloudm":"Sample",
        "eladeal":"Sample",
        "eladealm":"Sample",
        "esadeal":"Sample",
        "esadealm":"Sample",
        "zsw":"Sample",
        "zswm":"Sample",
        "turboinst":"Sample",
        "turboinstm":"Sample",
        "igf":"Sample",
        "igfm":"Sample",
        "explabs":"Sample",
        "explabsm":"Sample",
        "csmsw":"Sample",
        "csmswm":"Sample",
        "csmcloud":"Sample",
    },
    {
        "shortname":"Demonstration",
        "gbg":"Demonstration",
        "crosstps":"Demonstration",
        "crosstpsm":"Demonstration",
        "mgexec":"Demonstration",
        "mgexecm":"Demonstration",
        "silablead":"Demonstration",
        "silableadm":"Demonstration",
        "solarch":"Demonstration",
        "solarchm":"Demonstration",
        "bpsdaa":"Demonstration",
        "bpsdaam":"Demonstration",
        "bpssec":"Demonstration",
        "bpssecm":"Demonstration",
        "bpssus":"Demonstration",
        "bpssusm":"Demonstration",
        "bpsz":"Demonstration",
        "bpszm":"Demonstration",
        "bpspow":"Demonstration",
        "bpspowm":"Demonstration",
        "bpsstor":"Demonstration",
        "bpsstorm":"Demonstration",
        "bpscloud":"Demonstration",
        "bpscloudm":"Demonstration",
        "crosspts":"Demonstration",
        "crossptsm":"Demonstration",
        "ptsda":"Demonstration",
        "ptsdam":"Demonstration",
        "ptsauto":"Demonstration",
        "ptsautom":"Demonstration",
        "ptssec":"Demonstration",
        "ptssecm":"Demonstration",
        "ptssus":"Demonstration",
        "ptssusm":"Demonstration",
        "ptsz":"Demonstration",
        "ptszm":"Demonstration",
        "ptspow":"Demonstration",
        "ptspowm":"Demonstration",
        "ptsstor":"Demonstration",
        "ptsstorm":"Demonstration",
        "ptscloud":"Demonstration",
        "ptscloudm":"Demonstration",
        "eladeal":"Demonstration",
        "eladealm":"Demonstration",
        "esadeal":"Demonstration",
        "esadealm":"Demonstration",
        "zsw":"Demonstration",
        "zswm":"Demonstration",
        "turboinst":"Demonstration",
        "turboinstm":"Demonstration",
        "igf":"Demonstration",
        "igfm":"Demonstration",
        "explabs":"Demonstration",
        "explabsm":"Demonstration",
        "csmsw":"Demonstration",
        "csmswm":"Demonstration",
        "csmcloud":"Demonstration",
    },

]


# Schema for table “SERVICECOVERAGES"
# Set default schema to "SERVICECOVERAGES"
class CoverageModel(db.Model):
    __tablename__ = 'SERVICECOVERAGES'
    __table_args__ = TABLE_ARGS
    cid = db.Column('CID',db.Integer, primary_key=True)
    shortname = db.Column('PARTNAME',db.String(255))
    gbg = db.Column('GBG',db.String(255))
    crosstps = db.Column('CROSSTPS',db.String(255))
    crosstpsm = db.Column('CROSSTPSMGR',db.String(255))
    mgexec = db.Column('MGEXEC',db.String(255))
    mgexecm = db.Column('MGEXECMGR',db.String(255))
    silablead = db.Column('SILABLEAD',db.String(255))
    silableadm = db.Column('SILABLEADMGR',db.String(255))
    solarch = db.Column('SOLARCH',db.String(255))
    solarchm = db.Column('SOLARCHMGR',db.String(255))
    bpsdaa = db.Column('BPSDAA',db.String(255))
    bpsdaam = db.Column('BPSDAAMGR',db.String(255))
    bpssec = db.Column('BPSSEC',db.String(255))
    bpssecm = db.Column('BPSSECMGR',db.String(255))
    bpssus = db.Column('BPSSUS',db.String(255))
    bpssusm = db.Column('BPSSUSMGR',db.String(255))
    bpsz = db.Column('BPSZ',db.String(255))
    bpszm = db.Column('BPSZMGR',db.String(255))
    bpspow = db.Column('BPSPOW',db.String(255))
    bpspowm = db.Column('BPSPOWMGR',db.String(255))
    bpsstor = db.Column('BPSSTOR',db.String(255))
    bpsstorm = db.Column('BPSSTORMGR',db.String(255))
    bpscloud = db.Column('BPSCLOUD',db.String(255))
    bpscloudm = db.Column('BPSCLOUDMGR',db.String(255))
    crosspts = db.Column('CROSSPTS',db.String(255))
    crossptsm = db.Column('CROSSPTSMGR',db.String(255))
    ptsda = db.Column('PTSDA',db.String(255))
    ptsdam = db.Column('PTSDAMGR',db.String(255))
    ptsauto = db.Column('PTSAUTO',db.String(255))
    ptsautom = db.Column('PTSAUTOMGR',db.String(255))
    ptssec = db.Column('PTSSEC',db.String(255))
    ptssecm = db.Column('PTSSECMGR',db.String(255))
    ptssus = db.Column('PTSSUS',db.String(255))
    ptssusm = db.Column('PTSSUSMGR',db.String(255))
    ptsz = db.Column('PTSZ',db.String(255))
    ptszm = db.Column('PTSZMGR',db.String(255))
    ptspow = db.Column('PTSPOW',db.String(255))
    ptspowm = db.Column('PTSPOWMGR',db.String(255))
    ptsstor = db.Column('PTSSTOR',db.String(255))
    ptsstorm = db.Column('PTSSTORMGR',db.String(255))
    ptscloud = db.Column('PTSCLOUD',db.String(255))
    ptscloudm = db.Column('PTSCLOUDMGR',db.String(255))
    eladeal = db.Column('ELADEAL',db.String(255))
    eladealm = db.Column('ELADEALMGR',db.String(255))
    esadeal = db.Column('ESADEAL',db.String(255))
    esadealm = db.Column('ESADEALMGR',db.String(255))
    zsw = db.Column('ZSW',db.String(255))
    zswm = db.Column('ZSWMGR',db.String(255))
    turboinst = db.Column('TURBOINST',db.String(255))
    turboinstm = db.Column('TURBOINSTMGR',db.String(255))
    igf = db.Column('IGF',db.String(255))
    igfm = db.Column('IGFMGR',db.String(255))
    explabs = db.Column('EXPLABS',db.String(255))
    explabsm = db.Column('EXPLABSMGR',db.String(255))
    csmsw = db.Column('CSMSW',db.String(255))
    csmswm = db.Column('CSMSWMGR',db.String(255))
    csmcloud = db.Column('CSMCLOUD',db.String(255))


# the Python output for Coverages
class CoverageOutSchema(Schema):
    cid = Integer()
    shortname = String()
    gbg = String()
    crosstps = String()
    crosstpsm = String()
    mgexec = String()
    mgexecm = String()
    silablead = String()
    silableadm = String()
    solarch = String()
    solarchm = String()
    bpsdaa = String()
    bpsdaam = String()
    bpssec = String()
    bpssecm = String()
    bpssus = String()
    bpssusm = String()
    bpsz = String()
    bpszm = String()
    bpspow = String()
    bpspowm = String()
    bpsstor = String()
    bpsstorm = String()
    bpscloud = String()
    bpscloudm = String()
    crosspts = String()
    crossptsm = String()
    ptsda = String()
    ptsdam = String()
    ptsauto = String()
    ptsautom = String()
    ptssec = String()
    ptssecm = String()
    ptssus = String()
    ptssusm = String()
    ptsz = String()
    ptszm = String()
    ptspow = String()
    ptspowm = String()
    ptsstor = String()
    ptsstorm = String()
    ptscloud = String()
    ptscloudm = String()
    eladeal = String()
    eladealm = String()
    esadeal = String()
    esadealm = String()
    zsw = String()
    zswm = String()
    turboinst = String()
    turboinstm = String()
    igf = String()
    igfm = String()
    explabs = String()
    explabsm = String()
    csmsw = String()
    csmswm = String()
    csmcloud = String()

# the Python input for Coverages
class CoverageInSchema(Schema):
    shortname = String(required=True, validate=Length(0, 255))
    gbg = String(required=True, validate=Length(0, 255))
    crosstps = String(required=True, validate=Length(0, 255))
    crosstpsm = String(required=True, validate=Length(0, 255))
    mgexec = String(required=True, validate=Length(0, 255))
    mgexecm = String(required=True, validate=Length(0, 255))
    silablead = String(required=True, validate=Length(0, 255))
    silableadm = String(required=True, validate=Length(0, 255))
    solarch = String(required=True, validate=Length(0, 255))
    solarchm = String(required=True, validate=Length(0, 255))
    bpsdaa = String(required=True, validate=Length(0, 255))
    bpsdaam = String(required=True, validate=Length(0, 255))
    bpssec = String(required=True, validate=Length(0, 255))
    bpssecm = String(required=True, validate=Length(0, 255))
    bpssus = String(required=True, validate=Length(0, 255))
    bpssusm = String(required=True, validate=Length(0, 255))
    bpsz = String(required=True, validate=Length(0, 255))
    bpszm = String(required=True, validate=Length(0, 255))
    bpspow = String(required=True, validate=Length(0, 255))
    bpspowm = String(required=True, validate=Length(0, 255))
    bpsstor = String(required=True, validate=Length(0, 255))
    bpsstorm = String(required=True, validate=Length(0, 255))
    bpscloud = String(required=True, validate=Length(0, 255))
    bpscloudm = String(required=True, validate=Length(0, 255))
    crosspts = String(required=True, validate=Length(0, 255))
    crossptsm = String(required=True, validate=Length(0, 255))
    ptsda = String(required=True, validate=Length(0, 255))
    ptsdam = String(required=True, validate=Length(0, 255))
    ptsauto = String(required=True, validate=Length(0, 255))
    ptsautom = String(required=True, validate=Length(0, 255))
    ptssec = String(required=True, validate=Length(0, 255))
    ptssecm = String(required=True, validate=Length(0, 255))
    ptssus = String(required=True, validate=Length(0, 255))
    ptssusm = String(required=True, validate=Length(0, 255))
    ptsz = String(required=True, validate=Length(0, 255))
    ptszm = String(required=True, validate=Length(0, 255))
    ptspow = String(required=True, validate=Length(0, 255))
    ptspowm = String(required=True, validate=Length(0, 255))
    ptsstor = String(required=True, validate=Length(0, 255))
    ptsstorm = String(required=True, validate=Length(0, 255))
    ptscloud = String(required=True, validate=Length(0, 255))
    ptscloudm = String(required=True, validate=Length(0, 255))
    eladeal = String(required=True, validate=Length(0, 255))
    eladealm = String(required=True, validate=Length(0, 255))
    esadeal = String(required=True, validate=Length(0, 255))
    esadealm = String(required=True, validate=Length(0, 255))
    zsw = String(required=True, validate=Length(0, 255))
    zswm = String(required=True, validate=Length(0, 255))
    turboinst = String(required=True, validate=Length(0, 255))
    turboinstm = String(required=True, validate=Length(0, 255))
    igf = String(required=True, validate=Length(0, 255))
    igfm = String(required=True, validate=Length(0, 255))
    explabs = String(required=True, validate=Length(0, 255))
    explabsm = String(required=True, validate=Length(0, 255))
    csmsw = String(required=True, validate=Length(0, 255))
    csmswm = String(required=True, validate=Length(0, 255))
    csmcloud = String(required=True, validate=Length(0, 255))

# use with pagination
class CoverageQuerySchema(Schema):
    page = Integer(load_default=1)
    per_page = Integer(load_default=20, validate=Range(max=255))

class CoveragesOutSchema(Schema):
    coverages = List(Nested(CoverageOutSchema))
    pagination = Nested(PaginationSchema)

# register a callback to verify the token
@auth.verify_token  
def verify_token(token):
    if token in tokens:
        return tokens[token]
    else:
        return None

# retrieve a single coverage record by GBG
@app.get('/coverages/gbg/<string:gbg>')
@app.output(CoverageOutSchema)
@app.auth_required(auth)
def get_coverage_gbg(gbg):
    """Coverage record by GBG
    Retrieve a single coverage record by its GBG
    """
    search="%{}%".format(gbg)
    return CoverageModel.query.filter(CoverageModel.gbg.ilike(search)).first()

# retrieve a single coverage record by name
@app.get('/coverages/name/<string:short_name>')
@app.output(CoverageOutSchema)
@app.auth_required(auth)
def get_coverage_name(short_name):
    """Coverage record by name
    Retrieve a single coverage record by its short name
    """
    search="%{}%".format(short_name.replace("+","_"))
#    new_search=search.replace("+","%20")
#    fnew_search=new_search.format(short_name)
#    encoded_search=urllib.parse.quote(search).format(short_name)
    return CoverageModel.query.filter(CoverageModel.shortname.ilike(search)).first()


# get all coverages
@app.get('/coverages')
@app.input(CoverageQuerySchema, 'query')
#@app.input(CoverageInSchema(partial=True), location='query')
@app.output(CoveragesOutSchema)
@app.auth_required(auth)
def get_coverages(query):
    """all coverages
    Retrieve all coverage records
    """
    pagination = CoverageModel.query.paginate(
        page=query['page'],
        per_page=query['per_page']
    )
    return {
        'coverages': pagination.items,
        'pagination': pagination_builder(pagination)
    }

# create a coverage record
@app.post('/coverages')
@app.input(CoverageInSchema, location='json')
@app.output(CoverageOutSchema, 201)
@app.auth_required(auth)
def create_coverage(data):
    """Insert a new coverage record
    Insert a new coverage record with the given attributes. Its new GBG is returned.
    """
    coverage = CoverageModel(**data)
    db.session.add(coverage)
    db.session.commit()
    return coverage


# delete a coverage record
@app.delete('/coverages/gbg/<int:gbg>')
@app.output({}, 204)
@app.auth_required(auth)
def delete_coverage(gbg):
    """Delete a coverage record by GBG
    Delete a single coverage record identified by its GBG.
    """
    coverage = CoverageModel.query.get_or_404(gbg)
    db.session.delete(coverage)
    db.session.commit()
    return ''

# (re-)create the coverage table with sample records
@app.post('/database/recreate')
@app.input({'confirmation': Boolean(load_default=False)}, location='query')
#@app.output({}, 201)
@app.auth_required(auth)
def create_database(query):
    """Recreate the database schema
    Recreate the database schema and insert sample data.
    Request must be confirmed by passing query parameter.
    """
    if query['confirmation'] is True:
        db.drop_all()
        db.create_all()
        for e in sample_coverages:
            coverage = CoverageModel(**e)
            db.session.add(coverage)
        db.session.commit()
    else:
        abort(400, message='confirmation is missing',
            detail={"error":"check the API for how to confirm"})
        return {"message": "error: confirmation is missing"}
    return {"message":"database recreated"}


# default "homepage", also needed for health check by Code Engine
@app.get('/')
def print_default():
    """ Greeting
    health check
    """
    # returning a dict equals to use jsonify()
    return {'message': 'This is the Coverage API server'}


# Start the actual app
# Get the PORT from environment or use the default
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=int(port))
