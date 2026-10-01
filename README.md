# Your Daily Dose Pharmacy — Odoo 19 Community

**Version 19.0.1.0.0 · Spxcorp Limited**

A complete branded pharmacy storefront using the latest Noel’s Pharmacy five-page structure and the Value Seekers approach to Odoo’s native navigation. Red, blue, black and white branding comes from the supplied Your Daily Dose Pharmacy logo.

## Pages and shopping

| Page | Route |
| --- | --- |
| Home: three photo banners, categories, promotions and featured products | `/` (homepage `/ydd-home`) |
| Pharmacy Services, including common questions | `/pharmacy-services` |
| Wellness | `/wellness` |
| About Us | `/about-us` |
| Visit & Contact, WhatsApp and map directions | `/visit-us` |
| Native shop, categories and product pages | `/shop` |
| Native cart and checkout | `/shop/cart`, `/shop/checkout` |
| Native customer account and orders | `/my`, `/my/orders` |
| Native contact enquiry form | `/contactus` |

The original Odoo desktop/mobile header, search, account controls, cart and ecommerce controllers are retained. Branding follows the shopper across the native shop, product details, cart, checkout and account screens. The five marketing pages remain editable with Odoo’s Website editor.

## Install with Cloudpepper

Repository: `https://github.com/sheveioncallender-boop/yourdailydosepharmacy-webiste-.git`

1. Connect this repository to the intended **Odoo 19 Community** instance; select branch **main**.
2. Rebuild/redeploy the instance from Cloudpepper so Odoo loads the addon code.
3. In Odoo, enable developer mode and use **Apps → Update Apps List**.
4. Find and install **Your Daily Dose Pharmacy — Website & Shop** (technical name: `ydd_pharmacy_website`). The standard ecommerce/stock dependencies install automatically.
5. Open Website. The module sets the default website’s name, logo and homepage, and adds its navigation pages.
6. Review **Website → Configuration → Settings → Your Daily Dose Pharmacy** for contact details, hours, branding and sample-catalogue controls.

There is one addon folder directly at repository root. Point the addons path to the repository root, not its inner addon folder. Future code changes require a Cloudpepper redeploy followed by **Upgrade** of this app; Update Apps List alone does not apply XML changes.

This is a separate addon for the Your Daily Dose instance. It is not an upgrade of Noel’s or Value Seekers. Use it on the intended pharmacy website without the reference storefront modules installed. Installation targets `website.default_website`, not every website in a multi-website database.

## Included contact information

- Telephone: **+1 (868) 232-1432**
- WhatsApp: **+1 (868) 316-3281**
- Email: **yourdailydosepharmacy@outlook.com**
- Address: **#2 Scott Bushe & Charles Street, Port of Spain, Trinidad and Tobago**
- Facebook: <https://www.facebook.com/yddpharmacy/>
- Instagram: <https://www.instagram.com/yourdailydosepharmacy/>

Phone/email links, WhatsApp, socials and Google Maps directions are included. Sources and conflicting older entries are recorded in `docs/contact-sources.md`. Exact opening hours are left editable because published listings disagree. The pharmacy’s published delivery area is Port of Spain and environs, and Diego Martin; customers are asked to confirm delivery fees and availability with the pharmacy.

Website-specific contact fields avoid changing company accounting data. **Set the company’s matching business name, address, telephone and email in Odoo’s company settings as well**: the native `/contactus` page, enquiry recipient and invoices use those ordinary Odoo records. Configure outgoing email for contact enquiries. Clear the WhatsApp setting to hide its links.

## Sample catalogue and day-to-day editing

The same 12 photographed sample products and six ecommerce categories used in Noel’s are included. Products are native Odoo records, with descriptions, test prices and images; they are not fixed HTML cards. Categories are Skin Care, Bath & Body, Hair Care, Vitamins & Supplements, Baby Care, and Everyday Essentials.

- Featured products use Odoo’s visitor pricelist, currency and tax calculations.
- Unpublished/archived products and empty categories disappear from the homepage.
- Native product variants, quantity controls, cart and checkout remain under Odoo.
- Samples are non-stock-tracked goods; no fictitious stock receipts are created.
- Use **Featured on Your Daily Dose homepage** on products/categories to control the homepage selections.
- Use **Unpublish sample products** in Website settings when replacing the examples. Existing orders and product records are retained.
- Product and page seeds are `noupdate=1`: upgrades preserve prices, publication choices, content edits and contact settings.

No sample notices or badges are displayed to visitors. Confirm real catalogue images, prices, stock, TTD pricelist/company currency, applicable taxes, delivery methods and payment provider settings before taking live orders. This addon does not install a payment gateway, automatically enable insurance processing, or implement prescription uploads. Prescription enquiries are directed to the pharmacy.

## Validation

Static checks against a reviewed Odoo 19 revision cover XML schema, Python/QWeb/JavaScript syntax, SCSS compilation, local assets and the native-header inheritance chain. The GitHub Actions workflow performs a clean Odoo install with PostgreSQL, HTTP page/cart/checkout tests, publication/website isolation checks, contact-link tests, frontend asset compilation and an upgrade preservation check.

```sh
python -m pip install lxml Pillow libsass tinycss2
python scripts/validate_module.py --odoo-source /path/to/odoo19
```

Check the repository’s Actions results for runtime status. No customer Cloudpepper instance or production payment flow is changed by committing this module.

## Assets

The supplied logo is preserved exactly; CSS frames its whitespace in the header/footer. Three distinct real stock photographs (different from Noel’s), local fonts and the sample product photographs are bundled, so the website does not depend on image hotlinks. Pictured people are not represented as pharmacy employees. Credits and source URLs are in `ASSET_CREDITS.json`; font licences are bundled. Code is LGPL-3.0-or-later.

### Updating an existing installation to 19.0.1.1.0

Pull/rebuild the latest commit in Cloudpepper, then upgrade **Your Daily Dose Pharmacy — Website & Shop** in Apps. The versioned migration replaces the old bundled photos and removes the seeded sample paragraphs from existing pages/products while keeping merchant edits, prices, publication and contact settings. The homepage remains `/ydd-home`, served through the native website root `/`. Phone banners use a visible photo above the content; tablet and desktop layouts retain the split banner. Refresh the browser after the upgrade to load the new asset bundle.
