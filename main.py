import shopify
import os
import binascii
import logging
from fastapi import FastAPI, Request, params, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import (
    ORJSONResponse,
    RedirectResponse,
    JSONResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from config import Config as cfg
from models import *
from service import *

# TODO: add some sort of user and auth token to know which sotre
# TODO: add endpoint to list orders with template
# TODO: add function or endpoint to change order status to a specific status
# TODO: flow to request a new token
# TODO: how to revoke token
# TODO: add new scops to access
# TODO: item inventory
# TODO: change order level
# TODO: add webhook to be notifiued by orders


app = FastAPI(default_response_class=ORJSONResponse)
# app.mount("/static", StaticFiles(directory="templates"), name="static")
# templates = Jinja2Templates(directory="templates")
api_version = "2020-10"
shopify.Session.setup(
    api_key=cfg.SHOPIFY_CONFIG["API_KEY"], secret=cfg.SHOPIFY_CONFIG["API_SECRET"]
)


@AuthJWT.load_config
def get_config():
    return JwtSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/products")
async def products(request: Request, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    store = await get_store(current_user)

    with shopify.Session.temp(f"{store.name}.myshopify.com", api_version, store.token):
        products = shopify.Product.find()

    return [
        Product(
            title=product.title,
            status=product.status,
        )
        for product in products
    ]


@app.get("/orders")
async def orders(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    store = await get_store(current_user)

    with shopify.Session.temp(f"{store.name}.myshopify.com", api_version, store.token):
        orders = shopify.Order.find()

    return [
        Order(
            name=order.name,
            email=order.email,
        )
        for order in orders
    ]


@app.get("/install")
async def install(shop, user: str = ""):
    shop_url = f"{shop}.myshopify.com"
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    await add_user(state, user)

    newSession = shopify.Session(shop_url, api_version)
    auth_url = newSession.create_permission_url(
        cfg.SHOPIFY_CONFIG["SCOPE"], cfg.SHOPIFY_CONFIG["REDIRECT_URI"], state
    )
    logging.error(auth_url)
    return RedirectResponse(auth_url)


from fastapi import Request


@app.get("/auth")
async def auth(
    request: Request,
    shop: str,
    hmac: str,
    code: str,
    timestamp: str,
    state: str = None,
):
    session = shopify.Session(shop, api_version)
    parameters = {
        "shop": shop,
        "hmac": hmac,
        "code": code,
        "timestamp": timestamp,
        "state": state,
    }
    try:
        access_token = session.request_token(request.query_params)
        store = await get_store_with_name(shop)
        if store:
            await update_store(store.id, {"token": access_token})
        else:
            user = await get_user_with_token(state)
            await add_store(shop, access_token, str(user.id))

        return {"success": True}
    except Exception as e:
        return {"success": False}


@app.get("/")
async def ma():
    get_stores()