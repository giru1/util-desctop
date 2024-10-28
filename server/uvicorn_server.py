import logging
import multiprocessing
import time

from uvicorn import Config, Server
# from main import app

# logger = logging.getLogger(__name__)
# logging.basicConfig(
#     filename="uvicorn_server.log",
#     format="%(asctime)s %(levelname)-8s %(message)s",
#     level=logging.INFO,
# )

import json
import logging
import sys
import os
from fastapi.middleware.cors import CORSMiddleware

# for exe correct path
if getattr(sys, 'frozen', False):
    current_dir = os.path.join(sys._MEIPASS)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(current_dir)

parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse

from server.models.atol_device import AtolCashRegistr
from server.models.base import CashRegistr
from server.schemas.kkt import DeviceConnStatus, JsonTaskResponse, MethodError
from server.schemas.settings import Manufacture, Settings

drivers = {Manufacture.ATOL: AtolCashRegistr}  # Драйвер для Атол

settings = Settings()
settings_dir = os.getenv('APPDATA')


# print(current_dir)
# print(settings_dir.replace(os.sep, '/') + "/config.json")

settings.load_settings(file_name=settings_dir.replace(os.sep, '/') + '/config.json')
settings.lib_path = current_dir.replace(os.sep, '/') + '/fptr10.dll'
kkt: CashRegistr = drivers[settings.manufacture]("1", settings)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

api_v1 = APIRouter(prefix="/api/v1", tags=["API версия 1"])


@api_v1.get("/driver/settings", response_model=Settings)
def get_settings():
    
    return Settings(**kkt.driver_settings().model_dump())


@api_v1.post("/device/activate", responses={404: {"model": MethodError}})
def activate() -> None:
    if kkt.activate() != 0:
        return JSONResponse(
            status_code=404, content=MethodError(error=kkt.error()).model_dump()
        )

    return JSONResponse(content="success")


@api_v1.post("/device/deactivate", responses={404: {"model": MethodError}})
def deactivate():
    if kkt.deactivate() != 0:
        return JSONResponse(
            status_code=404, content=MethodError(error=kkt.error()).model_dump()
        )

    return JSONResponse(content="success")


@api_v1.get("/device/status", response_model=DeviceConnStatus)
def status():

    return int(kkt.conn_status())


@api_v1.post(
    "/requests/",
    response_model=JsonTaskResponse,
    responses={404: {"model": JsonTaskResponse}},
)
def create_request(**body: dict):
    status, result = kkt.create_request(json.dumps(body["body"]))

    if status:
        return JsonTaskResponse(request=body["body"], result=result)
    else:
        return JSONResponse(
            status_code=404,
            content=JsonTaskResponse(request=body["body"], result=result).model_dump(),
        )


app.include_router(api_v1)

def run_server(config: Config):
    config.app = app
    Server(config=config).run()

class UvicornServer(multiprocessing.Process):

    def __init__(self, config: Config):
        super().__init__()

        self.proc = None
        self.config = config
        self.server = Server(config=config)

    def run(self):
        self.server.run()
        

    def status(self):
        if self.proc and self.proc.is_alive():
            return True
        else:
            return False

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None

    def start(self):
        self.proc = multiprocessing.Process(target=run_server, kwargs={"config": self.config}, daemon=True)
        self.proc.start()
