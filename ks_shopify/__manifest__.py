# -*- coding: utf-8 -*-
{
    'name': "Odoo Shopify Connector",
    'summary': """Odoo Shopify Connector helps you automate all Shopify Odoo Integration operations seamlessly with the most 
                  advanced features of Product and Order Synchronization.
       """,
    'description': """
    Shopify Odoo Connector
    shopify odoo bridge
    shopify odoo integration
    connect odoo with shopify
    how to connect odoo with shopify
    multi channel shopify odoo bridge
    odoo shopify extension
    odoo integration with shopify
    odoo shopify
    shopify connector app
    shopify odoo app
    odoo ecommerce stores using shopify
    """,

    'author': "Ksolves India Ltd.",
    'website': "https://www.ksolves.com/",
    'category': 'Sales',
    'version': '14.0.1.3.0',
    'application': True,
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 325.7,
    'maintainer': 'Ksolves India Ltd.',
    'support': 'sales@ksolves.com',
    'images': ['static/description/ks_shopify.gif'],
    # any module necessary for this one to work correctly
    'live_test_url': 'https://shopify14.kappso.com/web/demo_login',

    'depends': ['base', 'mail', 'sale_management', 'stock', 'ks_base_connector'],
    'data': [
        'security/ir.model.access.csv',
        'security/ks_security.xml',
        # 'security/ks_shopify_commerce_model_security.xml',
        'views/ks_assets.xml',
        'reports/generate_report.xml',
        'reports/report.xml',
        'reports/ks_inst_sales_report.xml',
        'data/ks_automation.xml',
        'data/ks_order_status_data.xml',
        'data/ks_instance_data.xml',
        'data/ks_dashboard_data.xml',
        'data/ks_shopify_partner_data.xml',
        'data/ks_email_template.xml',
        'data/ks_product_product_data.xml',
        'wizards/ks_generic_config_view.xml',
        'wizards/ks_shopify_operations_views.xml',
        'wizards/ks_print_sales_report.xml',
        'wizards/ks_mapping_product_views.xml',
        'wizards/ks_mapping_res_partner_views.xml',
        'wizards/ks_base_instance_selection_views.xml',
        'wizards/ks_additional_data.xml',
        'views/ks_shopify_locations.xml',
        'views/ks_res_config.xml',
        'views/ks_shopify_auto_sale_workflow.xml',
        'views/ks_shopify_logs_views.xml',
        'views/ks_queue_job_views.xml',
        'views/ks_shopify_connector_instance_views.xml',
        'views/ks_res_partner_view.xml',
        'views/ks_shopify_partner_view.xml',
        'views/ks_delivery_transfers_view.xml',
        'views/ks_account_move_view.xml',
        'views/ks_product_attribute_view.xml',
        'views/ks_shopify_product_attr_value.xml',
        'views/ks_shopify_product_attribute_view.xml',
        'views/ks_shopify_product_variant_view.xml',
        'views/ks_shopify_product_images_view.xml',
        'views/ks_product_template_view.xml',
        'views/ks_shopify_product_template_view.xml',
        'views/ks_shopify_sale_order_view.xml',
        'views/ks_shopify_collections_views.xml',
        'views/ks_shopify_payment_gateway_view.xml',
        'views/ks_shopify_sale_order_reporting.xml',
        'views/ks_shopify_email_report.xml',
        'views/ks_shopify_discount_views.xml',
        'models/dashboard/ks_shopifydashboard_view.xml',
        'views/ks_shopify_menus.xml',
    ],

    'external_dependencies': {
    },
}
