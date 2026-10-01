"""Run inside an Odoo shell before and after upgrading the installed module."""
import os
phase = os.environ['YDD_UPGRADE_PHASE']
product = env.ref('ydd_pharmacy_website.sample_vanicream_daily')
home = env.ref('ydd_pharmacy_website.page_home').view_id.with_context(lang='en_US')
website = env.ref('website.default_website')
marker = '<!-- YDD merchant content preserved -->'
if phase == 'before':
    product.write({'list_price': 72.50, 'is_published': False})
    home.arch_db = home.arch_db.replace('</t>', marker + '</t>', 1)
    website.ydd_phone = '+1 868 555 0199'
    env.cr.commit()
else:
    assert product.list_price == 72.50
    assert not product.is_published
    assert marker in home.arch_db
    assert website.ydd_phone == '+1 868 555 0199'
    assert env['product.template'].search_count([('ydd_sample_product', '=', True)]) == 12
    print('PASS: upgrade preserves product price/publication, edited content and contact settings.')
