from odoo import SUPERUSER_ID, api
from odoo.addons.ydd_pharmacy_website.upgrade import refresh_existing_content


def migrate(cr, version):
    refresh_existing_content(api.Environment(cr, SUPERUSER_ID, {}))
