from odoo import fields, models
from odoo.fields import Domain


class Website(models.Model):
    _inherit = 'website'

    ydd_brand_enabled = fields.Boolean('Use Your Daily Dose branding', default=False)
    ydd_opening_hours = fields.Text('Opening hours', translate=True)
    ydd_catalogue_notice = fields.Boolean('Show sample catalogue notice', default=False)
    ydd_phone = fields.Char('Pharmacy telephone', default='+1 868 232-1432')
    ydd_whatsapp = fields.Char('WhatsApp number', default='18683163281', help='International digits only.')
    ydd_address = fields.Text('Pharmacy address', default='#2 Scott Bushe & Charles Street, Port of Spain, Trinidad and Tobago')
    ydd_email = fields.Char('Pharmacy email', default='yourdailydosepharmacy@outlook.com')

    def _ydd_whatsapp_url(self):
        self.ensure_one()
        digits = ''.join(c for c in (self.ydd_whatsapp or '') if c.isascii() and c.isdigit())
        return 'https://wa.me/' + digits if 7 <= len(digits) <= 15 else False

    def _ydd_maps_url(self):
        from urllib.parse import urlencode
        self.ensure_one()
        if not self.ydd_address:
            return False
        return 'https://www.google.com/maps/search/?' + urlencode({'api': '1', 'query': self.ydd_address})


    def _ydd_categories(self):
        """The same website/publication boundary as Odoo's normal category list."""
        self.ensure_one()
        Category = self.env['product.public.category'].with_context(website_id=self.id)
        if not self.ydd_brand_enabled or not self.has_ecommerce_access():
            return Category.browse()
        return Category.search(Domain.AND([
            self.website_domain(),
            [('ydd_homepage_featured', '=', True), ('has_published_products', '=', True)],
        ]), order='sequence, name, id', limit=12)

    def _ydd_featured_products(self):
        self.ensure_one()
        Product = self.env['product.template'].with_context(website_id=self.id)
        if not self.ydd_brand_enabled or not self.has_ecommerce_access():
            return Product.browse()
        # Explicit published/active predicates also apply when an editor previews the page.
        # No sudo: normal product/company/website access rules remain authoritative.
        return Product.search(Domain.AND([
            self.sale_product_domain(),
            [('active', '=', True), ('is_published', '=', True),
             ('ydd_homepage_featured', '=', True)],
        ]), order='website_sequence, id', limit=8)

    def _ydd_promo_product(self, category_xmlid):
        """Promotional cards disappear when their products are unpublished."""
        self.ensure_one()
        Product = self.env['product.template'].with_context(website_id=self.id)
        category = self.env.ref('ydd_pharmacy_website.' + category_xmlid, raise_if_not_found=False)
        if not category or not self.ydd_brand_enabled or not self.has_ecommerce_access():
            return Product.browse()
        return Product.search(Domain.AND([
            self.sale_product_domain(),
            [('active', '=', True), ('is_published', '=', True),
             ('public_categ_ids', 'child_of', category.id)],
        ]), order='website_sequence, id', limit=1)
