import locale
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup


def get_source() -> dict:
    url = os.getenv("SOURCE_URL")
    page = urlopen(url, cafile="assets/_.bcv.org.ve.crt")
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    dollar = locale.atof(
        (
            soup.css.select(
                "#dolar > div > div > div.col-sm-6.col-xs-6.centrado > strong"
            )[0].string
            or None
        )
    )
    euro = locale.atof(
        (
            soup.css.select(
                "#euro > div > div > div.col-sm-6.col-xs-6.centrado > strong"
            )[0].string
            or None
        )
    )
    ruble = locale.atof(
        (
            soup.css.select(
                "#rublo > div > div > div.col-sm-6.col-xs-6.centrado > strong"
            )[0].string
            or None
        )
    )
    yuan = locale.atof(
        (
            soup.css.select(
                "#yuan > div > div > div.col-sm-6.col-xs-6.centrado > strong"
            )[0].string
            or None
        )
    )
    lira = locale.atof(
        (
            soup.css.select(
                "#lira > div > div > div.col-sm-6.col-xs-6.centrado > strong"
            )[0].string
            or None
        )
    )

    currencies = {
        "USD": dollar,
        "EUR": euro,
        "RUB": ruble,
        "CNY": yuan,
        "TRY": lira,
    }

    return currencies
