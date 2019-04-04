import datetime

import app.bootstrap

from fastapi import FastAPI
from app.endpoints import setup_routes
from app.models import db

##
from fastapi import Depends, FastAPI
from starlette.requests import Request


#@app.middleware("http")
#async def echo_middleware(request: Request, call_next):
#    #request.state.db = SessionLocal()
#    t = str(datetime.datetime.now())
#    open("/tmp/t", "w").write(t)
#    print(t)
#    response = await call_next(request)
#    #request.state.db.close()
#    return response


def make_app():
    app = FastAPI()
    #app.add_middleware(DbTransactionMiddleware, db=db)

    setup_routes(app)
    return app


app = make_app()
