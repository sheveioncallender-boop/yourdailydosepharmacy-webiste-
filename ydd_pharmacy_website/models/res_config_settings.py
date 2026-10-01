from odoo import fields, models
from odoo.exceptions import AccessError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ydd_brand_enabled = fields.Boolean(related='website_id.ydd_brand_enabled', readonly=False)
    ydd_opening_hours = fields.Text(related='website_id.ydd_opening_hours', readonly=False)
    ydd_catalogue_notice = fields.Boolean(related='website_id.ydd_catalogue_notice', readonly=False)
    ydd_phone = fields.Char(related='website_id.ydd_phone', readonly=False)
    ydd_whatsapp = fields.Char(related='website_id.ydd_whatsapp', readonly=False)
    ydd_address = fields.Text(related='website_id.ydd_address', readonly=False)
    ydd_email = fields.Char(related='website_id.ydd_email', readonly=False)


    def action_ydd_unpublish_samples(self):
        self.ensure_one()
        if not self.env.user.has_group('website.group_website_designer'):
            raise AccessError(self.env._('Only website designers may manage the sample catalogue.'))
        products = self.env['product.template'].search([
            ('ydd_sample_product', '=', True),
            ('website_id', '=', self.website_id.id),
        ])
        products.write({'is_published': False})
        return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
            'title': self.env._('Sample catalogue unpublished'),
            'message': self.env._('Sample products remain available in the backend. Real products and orders are unchanged.'),
            'type': 'success', 'sticky': False,
        }}
