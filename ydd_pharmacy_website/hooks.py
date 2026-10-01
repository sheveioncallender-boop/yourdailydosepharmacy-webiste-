import base64
import json

from odoo.tools import file_open

MODULE = 'ydd_pharmacy_website'
SNAPSHOT = MODULE + '.installation_snapshot'
BRAND_NAME = 'Your Daily Dose Pharmacy'


def post_init_hook(env):
    """One-time setup. Module upgrades never reset page edits, products or branding."""
    website = env.ref('website.default_website')
    params = env['ir.config_parameter'].sudo()
    if params.get_param(SNAPSHOT):
        return
    with file_open(MODULE + '/static/src/img/ydd-logo.jpeg', 'rb') as logo_file:
        logo = base64.b64encode(logo_file.read())
    snapshot = {
        'website_id': website.id, 'homepage_url': website.homepage_url or False,
        'name': website.name, 'logo': website.logo.decode() if isinstance(website.logo, bytes) else website.logo or False,
        'menus': [],
    }
    website.write({
        'name': BRAND_NAME, 'logo': logo,
        'homepage_url': '/ydd-home', 'ydd_brand_enabled': True,
        'ydd_catalogue_notice': False,
    })
    menu_specs = [
        ('shop', 'Shop', '/shop', False, 15, ['/shop']),
        ('services', 'Our Services', '/pharmacy-services', 'page_services', 20, []),
        ('wellness', 'Wellness', '/wellness', 'page_wellness', 25, []),
        ('about', 'About Your Daily Dose', '/about-us', 'page_about', 30, ['/aboutus']),
        ('visit', 'Visit & Contact', '/visit-us', 'page_contact', 35, ['/contactus']),
    ]
    Menu = env['website.menu']
    for key, label, url, page_xmlid, sequence, aliases in menu_specs:
        page = env.ref(MODULE + '.' + page_xmlid) if page_xmlid else False
        existing = Menu.search([
            ('website_id', '=', website.id), ('parent_id', '=', website.menu_id.id),
            ('url', 'in', [url] + aliases),
        ], limit=1)
        if existing:
            if key == 'shop':
                continue  # Retain Odoo's existing shop menu unchanged.
            snapshot['menus'].append({
                'id': existing.id, 'name': existing.name, 'url': existing.url,
                'page_id': existing.page_id.id or False, 'sequence': existing.sequence,
                'installed_url': url,
            })
            existing.write({'name': label, 'url': url, 'page_id': page.id if page else False})
        else:
            menu = Menu.create({
                'name': label, 'url': url, 'page_id': page.id if page else False,
                'website_id': website.id, 'parent_id': website.menu_id.id, 'sequence': sequence,
            })
            env['ir.model.data'].create({
                'module': MODULE, 'name': 'menu_' + key, 'model': 'website.menu',
                'res_id': menu.id, 'noupdate': True,
            })
    params.set_param(SNAPSHOT, json.dumps(snapshot))


def uninstall_hook(env):
    params = env['ir.config_parameter'].sudo()
    raw = params.get_param(SNAPSHOT)
    if not raw:
        return
    snapshot = json.loads(raw)
    website = env['website'].browse(snapshot['website_id']).exists()
    if website:
        values = {}
        if website.homepage_url == '/ydd-home':
            values['homepage_url'] = snapshot['homepage_url']
        if website.name == BRAND_NAME:
            values['name'] = snapshot['name']
        with file_open(MODULE + '/static/src/img/ydd-logo.jpeg', 'rb') as logo_file:
            installed_logo = base64.b64encode(logo_file.read())
        if website.logo == installed_logo:
            values['logo'] = snapshot['logo']
        website.write(values)
    for old in snapshot.get('menus', []):
        menu = env['website.menu'].browse(old['id']).exists()
        if menu and menu.url == old['installed_url']:
            old_page = env['website.page'].browse(old['page_id']).exists() if old['page_id'] else False
            menu.write({'name': old['name'], 'page_id': old_page.id if old_page else False,
                        'url': old['url'], 'sequence': old['sequence']})
    params.search([('key', '=', SNAPSHOT)]).unlink()
