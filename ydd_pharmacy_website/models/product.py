from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ydd_homepage_featured = fields.Boolean('Feature on Your Daily Dose homepage', copy=False)
    ydd_sample_product = fields.Boolean('Your Daily Dose sample product', copy=False)
    ydd_sample_source_url = fields.Char('Sample reference', copy=False)


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    ydd_homepage_featured = fields.Boolean('Show in Your Daily Dose category circles', copy=False)
