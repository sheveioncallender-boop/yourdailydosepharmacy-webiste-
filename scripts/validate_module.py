"""Fast structural checks; real installation/HTTP tests run separately in CI."""
import argparse
import ast
from pathlib import Path
import re
import subprocess

from lxml import etree
from PIL import Image
import sass
import tinycss2


parser = argparse.ArgumentParser()
parser.add_argument('--odoo-source', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
module = root / 'ydd_pharmacy_website'
manifest = ast.literal_eval((module / '__manifest__.py').read_text())
schema = etree.RelaxNG(etree.parse(str(args.odoo_source / 'odoo/import_xml.rng')))
assert manifest['version'].startswith('19.0.')
assert 'website_sale_stock' in manifest['depends']
documents = []
for rel in manifest['data']:
    path = module / rel
    doc = etree.parse(str(path))
    schema.assertValid(doc)
    documents.append(doc)
    for node in doc.xpath('//*[@file]'):
        assert (root / node.get('file')).is_file(), node.get('file')
    for node in doc.xpath('//*[@src]'):
        value = node.get('src')
        if value.startswith('/ydd_pharmacy_website/'):
            assert (root / value.lstrip('/')).is_file(), value
    for node in doc.iter():
        for attribute, expression in node.attrib.items():
            if attribute in ('t-value', 't-if', 't-elif', 't-foreach', 't-out', 't-options') or attribute.startswith('t-att-'):
                ast.parse(expression, mode='eval')
for path in module.rglob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
for assets in manifest['assets'].values():
    for rel in assets:
        rel = rel[-1] if isinstance(rel, (list, tuple)) else rel
        path = root / rel
        assert path.is_file(), rel
        if path.suffix in ('.scss', '.css'):
            css = sass.compile(filename=str(path)) if path.suffix == '.scss' else path.read_text()
            errors = [item for item in tinycss2.parse_stylesheet(css) if item.type == 'error']
            assert not errors, (rel, errors)
            for local in re.findall(r'url\([\'\"]?(/ydd_pharmacy_website/[^)\'\"]+)', css):
                assert (root / local.lstrip('/')).is_file(), local
        elif path.suffix == '.js':
            subprocess.run(['node', '--input-type=module', '--check'], input=path.read_text(), text=True, check=True)
for path in (module / 'static/src/img').iterdir():
    with Image.open(path) as img:
        img.verify()
    if path.suffix == '.jpg':
        assert Image.open(path).format == 'JPEG', path
catalogue = etree.parse(str(module / 'data/catalog.xml'))
pages = etree.parse(str(module / 'data/pages.xml'))
assert len(catalogue.xpath('//record[@model="product.template"]')) == 12
assert len(catalogue.xpath('//record[@model="product.public.category"]')) == 6
assert len(pages.xpath('//record[@model="website.page"]')) == 5
assert catalogue.xpath('/odoo/data[@noupdate="1"]')
assert pages.xpath('/odoo/data[@noupdate="1"]')
layout = etree.parse(str(module / 'views/layout.xml'))
assert not layout.xpath('//header')  # Native header is inherited intact.
assert not layout.xpath('//xpath[@position="replace" and (@expr="//header" or @expr="//header[@id=\'top\']")]')
assert not (module / 'controllers').exists()  # No replacement ecommerce routes.
print('PASS: XML schema, QWeb expressions, Python/JS syntax, SCSS, local assets, native-header boundary, 12 products, 6 categories, 5 one-time pages.')

from check_native_templates import validate_native_templates
validate_native_templates(args.odoo_source, module)
