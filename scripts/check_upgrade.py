"""Run inside an Odoo shell before and after upgrading the installed module."""
import os
from odoo.addons.ydd_pharmacy_website.upgrade import SAMPLE_PARAGRAPH
phase = os.environ['YDD_UPGRADE_PHASE']
product = env.ref('ydd_pharmacy_website.sample_vanicream_daily')
home = env.ref('ydd_pharmacy_website.page_home').view_id.with_context(lang='en_US')
website = env.ref('website.default_website')
marker = '<!-- YDD merchant content preserved -->'
if phase == 'before':
    product.write({'list_price': 72.50, 'is_published': False})
    home.arch_db = home.arch_db.replace('</t>', marker + '</t>', 1)
    home.arch_db = home.arch_db.replace('family-outdoors.jpg', 'family.jpg')
    product.website_description = '<p>Merchant product details.</p>' + SAMPLE_PARAGRAPH
    website.ydd_catalogue_notice = True
    # Recreate the prior release version to exercise the real versioned migration.
    env['ir.module.module'].search([('name', '=', 'ydd_pharmacy_website')]).write({'latest_version': '19.0.1.0.0'})
    website.ydd_phone = '+1 868 555 0199'
    env.cr.commit()
else:
    assert product.list_price == 72.50
    assert not product.is_published
    assert marker in home.arch_db
    assert website.ydd_phone == '+1 868 555 0199'
    assert 'family-outdoors.jpg' in home.arch_db
    assert '/img/family.jpg' not in home.arch_db
    assert 'Merchant product details.' in product.website_description
    assert 'Sample product for website testing' not in product.website_description
    assert not website.ydd_catalogue_notice
    assert env['product.template'].search_count([('ydd_sample_product', '=', True)]) == 12
    print('PASS: versioned migration refreshes photography and removes notices while preserving merchant edits.')
