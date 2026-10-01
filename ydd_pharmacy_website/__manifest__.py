{
    'name': "Your Daily Dose Pharmacy — Website & Shop",
    'version': '19.0.1.0.0',
    'summary': 'Your Daily Dose design, native Odoo eCommerce, category cards and a sample catalogue',
    'category': 'Website/eCommerce',
    'author': 'Spxcorp Limited',
    'website': 'https://spxcorp.net',
    'license': 'LGPL-3',
    'depends': ['website_sale_stock'],
    'data': [
        'views/backend_views.xml',
        'views/layout.xml',
        'views/commerce_blocks.xml',
        'data/catalog.xml',
        'data/pages.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'ydd_pharmacy_website/static/src/css/brand_variables.scss'),
        ],
        'web.assets_frontend': [
            'ydd_pharmacy_website/static/src/css/fonts.css',
            'ydd_pharmacy_website/static/src/css/pages.scss',
            'ydd_pharmacy_website/static/src/css/brand.scss',
            'ydd_pharmacy_website/static/src/css/storefront.scss',
            'ydd_pharmacy_website/static/src/js/banner.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': True,
}
