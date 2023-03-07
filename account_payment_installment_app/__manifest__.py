# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Installment App',
    "author": "Edge Technologies",
    'version': '14.0.1.0',
    'live_test_url': "https://youtu.be/t6wtzL07MTI",
    "images":['static/description/main_screenshot.png'],
    'summary': "Account Payment Installment for payment installment for accounting payment for installment pay invoice on installment pay bill on installment pay invoice on batch partial invoice payment partial installment on sales order installation sale installment ",
    'description': """ This Odoo Account Payment Installments module 
                       helps users to make payments in installments in 
                       the Sale Order. Users can set the Durations months 
                       and down Payments Amount and also print the PDF report in Invoice for the Payment Installments.
    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','account','purchase','stock'],
    'data': [
            'security/ir.model.access.csv',
            'security/res_group.xml',
            'data/data.xml',
            'wizard/account_payment_installment_wizard.xml',
            'views/inherit_sale_order_view.xml',
            'views/inherit_account_move_view.xml',
            'views/cron_data.xml',
            'report/sale_installment_template.xml',
            'report/account_installment_template.xml',
            ],
    'installable': True,
    'auto_install': False,
    'price': 30,
    'currency': "EUR",
    'category': 'Accounting',

}

