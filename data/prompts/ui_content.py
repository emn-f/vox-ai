from datetime import datetime

from src.i18n import get_saudacao, get_sidebar_body, get_sidebar_footer

ANO_ATUAL = datetime.today().year

SAUDACAO = get_saudacao("pt")

SIDEBAR_BODY = get_sidebar_body("pt")

SIDEBAR_FOOTER = get_sidebar_footer("pt")
