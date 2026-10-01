from lxml import html

from odoo.tests import HttpCase, tagged
from odoo.addons.website_sale.tests.common import MockRequest
from ..hooks import post_init_hook


@tagged('post_install', '-at_install', 'ydd_pharmacy')
class TestYddWebsite(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website.write({'domain': False, 'ecommerce_access': 'everyone'})
        cls.sample = cls.env.ref('ydd_pharmacy_website.sample_vanicream_daily')
        cls.category = cls.env.ref('ydd_pharmacy_website.category_1')

    def test_seed_records_and_idempotent_setup(self):
        samples = self.env['product.template'].search([('ydd_sample_product', '=', True)])
        self.assertEqual(len(samples), 12)
        self.assertTrue(all(p.image_1920 and p.website_description and p.public_categ_ids for p in samples))
        self.assertEqual(self.website.homepage_url, '/ydd-home')
        menu_count = self.env['website.menu'].search_count([('website_id', '=', self.website.id)])
        self.sample.list_price = 72.50
        post_init_hook(self.env)
        self.assertEqual(self.sample.list_price, 72.50)
        self.assertEqual(self.env['website.menu'].search_count([('website_id', '=', self.website.id)]), menu_count)

    def test_publishing_and_website_isolation(self):
        public = self.website.with_user(self.website.user_id).with_context(website_id=self.website.id)
        with MockRequest(public.env, website=public):
            self.assertIn(self.sample.id, public._ydd_featured_products().ids)
            self.sample.is_published = False
            self.assertNotIn(self.sample.id, public._ydd_featured_products().ids)
            self.sample.is_published = True
            self.sample.active = False
            self.assertNotIn(self.sample.id, public._ydd_featured_products().ids)
        other = self.env['website'].create({'name': 'Another store', 'company_id': self.website.company_id.id, 'ydd_brand_enabled': True})
        other_public = other.with_user(other.user_id).with_context(website_id=other.id)
        with MockRequest(other_public.env, website=other_public):
            self.assertNotIn(self.category.id, other_public._ydd_categories().ids)
            self.assertNotIn(self.sample.id, other_public._ydd_featured_products().ids)

    def test_empty_categories_and_private_shop(self):
        public = self.website.with_user(self.website.user_id).with_context(website_id=self.website.id)
        self.category.product_tmpl_ids.write({'is_published': False})
        with MockRequest(public.env, website=public):
            self.assertNotIn(self.category.id, public._ydd_categories().ids)
            self.assertFalse(public._ydd_promo_product('category_1'))
        self.website.ecommerce_access = 'logged_in'
        with MockRequest(public.env, website=public):
            self.assertFalse(public._ydd_featured_products())
            self.assertFalse(public._ydd_categories())

    def test_pages_header_and_native_shop(self):
        for path in ['/', '/pharmacy-services', '/wellness', '/about-us', '/visit-us', '/shop', self.sample.website_url]:
            with self.subTest(path=path):
                response = self.url_open(path, timeout=60)
                self.assertEqual(response.status_code, 200, response.text[:1000])
                document = html.fromstring(response.content)
                self.assertEqual(len(document.xpath('//header[@id="top"]')), 1)
                self.assertTrue(document.xpath('//header//a[@href="/shop/cart"]'))
                self.assertFalse(document.xpath('//header//button[contains(@class,"menu-toggle")]'))
                self.assertTrue(document.xpath('//header//*[contains(concat(" ", @class, " "), " ydd-topbar ")]'))
        home = html.fromstring(self.url_open('/').content)
        self.assertEqual(len(home.xpath('//a[contains(@class,"ydd-category")]')), 6)
        self.assertEqual(len(home.xpath('//div[contains(concat(" ",@class," ")," banner-slide ")]')), 3)

    def test_native_cart_and_checkout(self):
        self.url_open('/')  # Establish the standard Odoo visitor/session.
        result = self.make_jsonrpc_request('/shop/cart/add', {
            'product_template_id': self.sample.id,
            'product_id': self.sample.product_variant_id.id,
            'quantity': 2,
        }, timeout=60)
        self.assertEqual(result['quantity'], 2)
        cart = self.url_open('/shop/cart', timeout=60)
        self.assertEqual(cart.status_code, 200)
        self.assertIn(self.sample.name, html.fromstring(cart.content).text_content())
        checkout = self.url_open('/shop/checkout', timeout=60)
        self.assertEqual(checkout.status_code, 200)
        self.assertNotIn('Traceback', checkout.text)

    def test_company_phone_and_desktop_cart_order(self):
        self.website.ydd_phone = '+1 868 555 0199'
        page = html.fromstring(self.url_open('/').content)
        self.assertTrue(page.xpath('//header//a[@href="tel:+1 868 555 0199"]'))
        self.assertNotIn('555-555-5556', page.xpath('//header')[0].text_content())
        desktop_cart = page.xpath('//*[@id="o_main_nav"]//*[contains(concat(" ", @class, " "), " o_wsale_my_cart ")]')
        self.assertEqual(len(desktop_cart), 1)
        self.assertTrue(desktop_cart[0].xpath('preceding-sibling::*'))
        self.assertEqual(page.xpath('//*[contains(concat(" ", @class, " "), " ydd-home ")]')[0].get('id'), 'wrap')

    def test_contact_links_and_safe_whatsapp(self):
        page = html.fromstring(self.url_open('/visit-us').content)
        self.assertTrue(page.xpath('//a[@href="tel:+1 868 232-1432"]'))
        self.assertTrue(page.xpath('//a[@href="mailto:yourdailydosepharmacy@outlook.com"]'))
        self.assertTrue(page.xpath('//a[@href="https://wa.me/18683163281"]'))
        self.assertTrue(page.xpath('//a[@href="https://www.facebook.com/yddpharmacy/"]'))
        self.assertTrue(page.xpath('//a[@href="https://www.instagram.com/yourdailydosepharmacy/"]'))
        self.assertIn('#2 Scott Bushe & Charles Street', page.text_content())
        self.website.ydd_whatsapp = ''
        self.assertFalse(self.website._ydd_whatsapp_url())
        self.website.ydd_whatsapp = '+1 (868) 316-3281'
        self.assertEqual(self.website._ydd_whatsapp_url(), 'https://wa.me/18683163281')

    def test_unpublish_sample_catalogue_preserves_real_products(self):
        real = self.env['product.template'].create({
            'name': 'Real stock product', 'website_id': self.website.id,
            'is_published': True, 'list_price': 125.0,
        })
        settings = self.env['res.config.settings'].create({'website_id': self.website.id})
        settings.action_ydd_unpublish_samples()
        samples = self.env['product.template'].search([('ydd_sample_product', '=', True)])
        self.assertEqual(len(samples), 12)
        self.assertFalse(any(samples.mapped('is_published')))
        self.assertTrue(real.is_published)
        self.assertEqual(real.list_price, 125.0)

    def test_frontend_asset_compilation(self):
        page = html.fromstring(self.url_open('/').content)
        assets = [href for href in page.xpath('//link[@rel="stylesheet"]/@href')
                  if '/web/assets/' in href]
        self.assertTrue(assets)
        for href in assets:
            response = self.url_open(href, timeout=120)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('style compilation failed', response.text.lower())
            self.assertNotIn('sass.compileerror', response.text.lower())
