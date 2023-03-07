# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': "Customer Credit Limit",
    'version': "14.0.0.1",
    'summary': "Customer Credit Limit Assign/Hold/Blocking. credit limit on partner.",
    'category': 'Sales',
    'description': """
        This modules helps you to check the Customer Credit Limit on Sale order.
        Credit Limit
        Customer Credit
        credit work flow
        sale limit
        sale credit
        partner credit
        credit partner
        credit customer
        customer credit limit
        AR on sales,
        overdue warning,
        customer credit warning
        credit limit hold
        block credit limit
        block partner
        credit limit cross email notification
        exceeded credit limit email notification
        customer credit approval,credit limit on partner
        partner overdue
        partner total receivable
        customer credit limit against account
        customer credit limit against AR
        customer credit limit against account receivable
        Total Account Receivable amount on sale
        
       
    """,
    'author': "Sitaram",
    'website':"sitaramsolutions.in",
    'depends': ['base', 'sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/inherited_partner.xml',
        'views/inherited_sale_order.xml',
        'wizard/credit_limit_info_wizard.xml'
    ],
    'live_test_url':'https://youtu.be/YtZuFJntEDY',
    'images': ['static/description/banner.png'],
    "price": 20,
    "currency": 'EUR',
    'demo': [],
    "license": "OPL-1",
    'installable': True,
    'auto_install': False,
}
