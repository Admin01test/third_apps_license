{
    'name': 'Odoo Is a Customer, Is a Vendor',
    'version': '1.0.0',
    'author': 'FreelancerApps',
    'category': 'Tools',
    'depends': ['base', 'sale_management', 'purchase'],
    'summary': 'Provide same field Is Customer Is Vendor into the partner Customer Vendor Field customer field is supplied field supplier options customer options wehsite hide menu checklist readonly',
    'description': '''
Odoo13 Is a Customer, Is a Vendor
=================================
This module provide two fields <b>Is a Customer, Is a Vendor</b> in to the partner to identify contact is customer/vendor or not. 
In Odoo14 those fields are removed. We have added them back same as like older version.

KEY FEATURES:
-------------
    * Easy To Use.
    * Added Is Customer, Is vendor checkbox Into The Partner Form For Identification.
    * User Can Manually Set/ Unset Customer and Vendor Checkbox.
    * Added Customer Filter In Sale Order.
    * Added Vendor Filter In Purchase Order.
    * Added translations for partner type, is customer and is supplier fields.
''',
    'data': ['views/res_partner_view.xml'],
    'post_init_hook': 'update_old_partners',
    'images': ['static/description/is_customer_is_vendor_banner.gif'],
    'price': 4.99,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
