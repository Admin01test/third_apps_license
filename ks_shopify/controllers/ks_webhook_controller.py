# -*- coding: utf-8 -*-

import json
import base64
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import Root, HttpRequest
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class KsShopifyWebhookHandler(http.Controller):
    @http.route(['/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/collections/create',
                 '/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/collections/update'], auth='none',
                type='json', csrf=False, methods=['POST'])
    def create_update_collections_webhook(self, db, shopify_instance, uid, **post):
        try:
            encoded_db = db.strip()
            decoded_db = base64.urlsafe_b64decode(encoded_db)
            request.session.db = str(decoded_db, "utf-8")
            if uid:
                request.session.uid = int(uid)
                request.env.user = request.env['res.users'].browse(int(uid))
                request.env.uid = int(uid)
            data = request.jsonrequest
            if data:
                self._ks_check_user()
                if shopify_instance:
                    shopify_instance = request.env['ks.shopify.connector.instance'].sudo().search(
                        [('id', '=', shopify_instance)],
                        limit=1)
                    if shopify_instance and data:
                        request.env.company = shopify_instance.ks_company_id
                        request.env.companies = shopify_instance.ks_company_id
                        request.env['ks.shopify.custom.collections'].sudo().ks_manage_shopify_collections_import(
                            shopify_instance, data)
                        return 'ok'
            return 'ok'
        except Exception as e:
            _logger.info("Create/Update of Collections failed with exception through webhook failed " + str(e))
            return request.not_found()

    @http.route(['/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/customers/create',
                 '/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/customers/update'], type='json',
                auth='none', csrf=False, methods=['POST'])
    def create_customers_webhook(self, shopify_instance, db, uid, **post):
        try:
            encoded_db = db.strip()
            decoded_db = base64.urlsafe_b64decode(encoded_db)
            request.session.db = str(decoded_db, "utf-8")
            if uid:
                request.session.uid = int(uid)
                request.env.user = request.env['res.users'].browse(int(uid))
                request.env.uid = int(uid)

            data = request.jsonrequest
            if data:
                self._ks_check_user()
                if shopify_instance:
                    shopify_instance = request.env['ks.shopify.connector.instance'].sudo().search(
                        [('id', '=', shopify_instance)],
                        limit=1)
                    if shopify_instance and data:
                        request.env.company = shopify_instance.ks_company_id
                        request.env.companies = shopify_instance.ks_company_id
                        request.env['ks.shopify.partner'].sudo().ks_manage_shopify_customer_import(shopify_instance, data)
                        return 'ok'
                    return 'ok'
        except Exception as e:
            _logger.info("Create/Update of Customers failed through webhook failed " + str(e))
            return Response("The requested URL was not found on the server.", status=404)

    @http.route(['/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/products/create',
                 '/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/products/update'], type='json',
                auth='none', csrf=False,
                methods=['POST'])
    def create_update_product_webhook(self, shopify_instance, db, uid, **post):
        try:
            encoded_db = db.strip()
            decoded_db = base64.urlsafe_b64decode(encoded_db)
            request.session.db = str(decoded_db, "utf-8")
            if uid:
                request.session.uid = int(uid)
                request.env.user = request.env['res.users'].browse(int(uid))
                request.env.uid = int(uid)

            data = request.jsonrequest
            if data:
                self._ks_check_user()
                if shopify_instance:
                    shopify_instance = request.env['ks.shopify.connector.instance'].sudo().search(
                        [('id', '=', shopify_instance)],
                        limit=1)
                    if shopify_instance and data:
                        request.env.company = shopify_instance.ks_company_id
                        request.env.companies = shopify_instance.ks_company_id
                        ##TODO: Handle product import manager function here
                        request.env['ks.shopify.product.template'].sudo().ks_manage_shopify_product_template_import(shopify_instance, data)
                    else:
                        _logger.info("Fatal Error with the wcapi()")
            return 'ok'
        except Exception as e:
            _logger.info("Create/Update of product failed through webhook failed " + str(e))
            return request.not_found()

    @http.route(['/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/orders/create',
                 '/shopify_hook/<string:db>/<string:uid>/<int:shopify_instance>/orders/update'], type='json', auth='none', csrf=False,
                methods=['POST'])
    def create_update_order_webhook(self, shopify_instance, db, uid, **post):
        try:
            encoded_db = db.strip()
            decoded_db = base64.urlsafe_b64decode(encoded_db)
            request.session.db = str(decoded_db, "utf-8")
            if uid:
                request.session.uid = int(uid)
                request.env.user = request.env['res.users'].browse(int(uid))
                request.env.uid = int(uid)
            data = request.jsonrequest
            if data:
                self._ks_check_user()
                if shopify_instance:
                    shopify_instance = request.env['ks.shopify.connector.instance'].sudo().search(
                        [('id', '=', shopify_instance)],
                        limit=1)
                    if shopify_instance and data:
                        request.env.company = shopify_instance.ks_company_id
                        request.env.companies = shopify_instance.ks_company_id
                        sale_order_exist = request.env['sale.order'].sudo().search([('ks_shopify_order_id', '=', data.get('id')), ('ks_shopify_instance', '=', shopify_instance.id)])
                        if sale_order_exist:
                            sale_order_exist.ks_shopify_import_order_update(data)
                        else:
                            if not data.get('cancelled_at'):
                                sale_order_exist.ks_shopify_import_order_create(data, shopify_instance)
                        # TODO: Add manager function calling here

            return 'ok'
        except Exception as e:
            _logger.info("Create/Update of order failed through webhook failed " + str(e))
            return request.not_found()

    def _ks_check_user(self):
        if request.env.user.has_group('base.group_public'):
            request.env.user = request.env['res.users'].browse(SUPERUSER_ID)
            request.env.uid = SUPERUSER_ID
        return request.env.user


old_get_request = Root.get_request


def get_request(self, httprequest):
    is_json = httprequest.args.get('jsonp') or httprequest.mimetype in ("application/json", "application/json-rpc")
    httprequest.data = {}
    shopify_hook_path = ks_match_the_url_path(httprequest.path)
    if shopify_hook_path and is_json:
        request = httprequest.get_data().decode(httprequest.charset)
        httprequest.data = json.loads(request)
        return HttpRequest(httprequest)
    return old_get_request(self, httprequest)


Root.get_request = get_request


def ks_match_the_url_path(path):
    if path:
        path_list = path.split('/')
        if path_list[1] == 'woo_hook' and path_list[5] in ['customer', 'product', 'collections'
                                                                                  'order'] and path_list[6] in [
            'create',
            'update']:
            return True
        else:
            return False
