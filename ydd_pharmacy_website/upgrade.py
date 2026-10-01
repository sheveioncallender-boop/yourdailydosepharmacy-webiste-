"""Targeted updates for existing editable records; never reload seed data."""
import re

MODULE = 'ydd_pharmacy_website'
SAMPLE_PARAGRAPH = ('<p><strong>Sample product for website testing. </strong>'
                    'Price, availability, pack details and product image must be '
                    'confirmed by Your Daily Dose before live sales.</p>')
PHOTOS = {
    'family.jpg': ('family-outdoors.jpg', 'Family enjoying time together outdoors', 1800, 1312),
    'pharmacist.jpg': ('pharmacy-care.jpg', 'Smiling pharmacist at a pharmacy counter', 1800, 1200),
    'wellness.jpg': ('active-living.jpg', 'Woman exercising outdoors in a park', 1800, 1200),
}


def replace_photos(arch):
    def replace(match):
        tag = match.group()
        for old, (new, alt, width, height) in PHOTOS.items():
            old_path = '/' + MODULE + '/static/src/img/' + old
            if old_path not in tag:
                continue
            tag = tag.replace(old_path, '/' + MODULE + '/static/src/img/' + new)
            for attribute, value in [('alt', alt), ('width', width), ('height', height)]:
                tag = re.sub(attribute + r'="[^"]*"', f'{attribute}="{value}"', tag)
        return tag
    return re.sub(r'<img\b[^>]*>', replace, arch)


def _update_translations(record, field_name, transform):
    # Snapshot each stored language, so no wholesale page/description reset is needed.
    translations = record._fields[field_name]._get_stored_translations(record) or {}
    active_languages = set(record.env['res.lang'].get_installed())
    active_languages = {code for code, _name in active_languages}
    for language, original in translations.items():
        if language not in active_languages:
            continue
        updated = transform(original)
        if updated != original:
            record.with_context(lang=language).write({field_name: updated})


def refresh_existing_content(env):
    keys = [MODULE + '.page_' + name for name in ['home', 'services', 'wellness', 'about', 'contact']]
    for view in env['ir.ui.view'].search([('key', 'in', keys)]):
        _update_translations(view, 'arch_db', replace_photos)
    seeds = env['ir.model.data'].search([
        ('module', '=', MODULE), ('model', '=', 'product.template'),
        ('name', '=like', 'sample_%'),
    ])
    for product in env['product.template'].browse(seeds.mapped('res_id')).exists():
        _update_translations(product, 'website_description', lambda text: text.replace(SAMPLE_PARAGRAPH, ''))
    website = env.ref('website.default_website', raise_if_not_found=False)
    if website and website.ydd_brand_enabled:
        website.ydd_catalogue_notice = False
