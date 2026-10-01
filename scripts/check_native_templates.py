"""Apply our XPaths using the actual Odoo 19 inheritance engine, without a DB."""
import copy
import html
from pathlib import Path

from lxml import etree


def validate_native_templates(source, module):
    engine = (source / 'odoo/tools/template_inheritance.py').read_text()
    for line in ('from odoo.tools.translate import LazyTranslate',
                 'from odoo.exceptions import ValidationError',
                 'from .misc import SKIPPED_ELEMENT_TYPES, html_escape'):
        engine = engine.replace(line, '')
    namespace = {
        'LazyTranslate': lambda *_: lambda message, *args: message % args if args else message,
        'ValidationError': ValueError,
        'SKIPPED_ELEMENT_TYPES': (etree._Comment, etree._ProcessingInstruction),
        'html_escape': html.escape,
    }
    exec(compile(engine, 'odoo19_template_inheritance', 'exec'), namespace)
    apply = namespace['apply_inheritance_specs']
    etree.FunctionNamespace(None)['hasclass'] = lambda ctx, *names: all(
        name in (ctx.context_node.get('class') or '').split() for name in names)

    def load(path):
        return etree.parse(str(source / path))

    def template(doc, key):
        return doc.xpath('//template[@id=$key]', key=key)[0]

    def modify(arch, spec):
        instructions = etree.Element('data')
        instructions.extend(copy.deepcopy(list(spec)))
        return apply(arch, instructions)

    web = load('addons/web/views/webclient_templates.xml')
    portal = load('addons/portal/views/portal_templates.xml')
    website = load('addons/website/views/website_templates.xml')
    sale = load('addons/website_sale/views/templates.xml')
    custom = etree.parse(str(module / 'views/layout.xml'))
    base = etree.Element('data')
    base.extend(copy.deepcopy(list(template(web, 'web.layout'))))
    for document, name in [(web, 'web.frontend_layout'), (portal, 'frontend_layout'),
                           (website, 'layout'), (sale, 'website_sale_layout')]:
        base = modify(base, template(document, name))
    headers = website.xpath('//template[@inherit_id="website.layout" and starts-with(@id,"template_header_")]')
    count = 0
    for header in headers:
        if header.get('id') in ('template_header_navlink_no_background',
                               'template_header_additional_color_primary',
                               'template_header_additional_color_secondary'):
            continue
        arch = modify(copy.deepcopy(base), header)
        for extension in sale.xpath('//template[@inherit_id=$ref]', ref='website.' + header.get('id')):
            arch = modify(arch, extension)
        if header.get('id') == 'template_header_default':
            arch = modify(arch, template(custom, 'ydd_header_order'))
            calls = arch.xpath('//div[@id="o_main_nav"]/ul/t')
            branded = [node.get('t-call') for node in calls if node.get('t-if') != 'not website.ydd_brand_enabled']
            assert branded.index('website.placeholder_header_search_box') < branded.index('portal.user_dropdown') < branded.index('website_sale.header_cart_link')
            assert branded.count('website_sale.header_cart_link') == 1
            user = arch.xpath('//t[@t-call="portal.user_dropdown"]')[0]
            assert user.get('_link_class.f') is None
        arch = modify(arch, template(custom, 'layout_brand'))
        assert len(arch.xpath('//header[@id="top"]')) == 1
        assert arch.xpath('//header//t[@t-call="website_sale.header_cart_link"]')
        assert arch.xpath('//header//t[@t-call="website.template_header_mobile"]')
        count += 1
    phone = modify(copy.deepcopy(template(website, 'website.placeholder_header_text_element')),
                   template(website, 'website.header_text_element'))
    phone = modify(phone, template(custom, 'ydd_native_phone'))
    assert len(phone.xpath('//t[@t-call="ydd_pharmacy_website.ydd_phone_link"]')) == 3
    modify(copy.deepcopy(template(portal, 'user_dropdown')), template(custom, 'ydd_account_label'))
    print(f'PASS: Odoo inheritance engine, {count} native header layouts, branded cart order and company phone.')
