# -*- coding: utf-8 -*-

from odoo import fields, models, _
import logging
_logger = logging.getLogger(__name__)


class KsProductAttributeValueExtended(models.Model):
    _inherit = "product.attribute.value"

    ks_connected_shopify_attribute_terms = fields.One2many('ks.shopify.pro.attr.value', 'ks_pro_attr_value',
                                                       string="Shopify Attribute Values Ids")


class KsShopifyProductAttributeModel(models.Model):
    _name = "ks.shopify.pro.attr.value"
    _rec_name = "ks_name"
    _description = "Shopify Product Attribute Value"

    ks_attribute_id = fields.Many2one('product.attribute', string="Attribute", ondelete='cascade',
                                      related='ks_pro_attr_value.attribute_id',
                                      index=True,
                                      help="The attribute cannot be changed once the value is used on at least one "
                                           "product.")
    ks_shopify_attribute_id = fields.Char('Shopify Attribute ID', readonly=True,
                                         help=_("the record id of the particular record defied in the Connector"))
    ks_shopify_instance = fields.Many2one("ks.shopify.connector.instance", string="Instance", readonly=True,
                                     help=_("Shopify Connector Instance reference"),
                                     ondelete='cascade')
    ks_pro_attr_value = fields.Many2one('product.attribute.value', string="Odoo Attribute Value", ondelete='cascade', help="Displays Odoo Attribute Value Name Reference")
    ks_name = fields.Char(string='Value', related="ks_pro_attr_value.name", translate=True, help="Displays Shopify Attribute Value Name")
    ks_mapped = fields.Boolean(string = "Manual Mapping", readonly = True)

    def ks_manage_value_preparation(self, instance, attribute_values):
        for value in attribute_values:
            product_attr_value_exist = self.check_if_already_prepared(instance, value)
            if not product_attr_value_exist:
                self.create_shopify_record(instance, value)
            else:
                self.update_shopify_record(instance, value)

    def ks_map_prepare_data_for_layer(self, instance, product_attribute_value):
        """
        """
        data = {
            "ks_pro_attr_value": product_attribute_value.id,
            "ks_shopify_instance": instance.id,
            "ks_attribute_id": product_attribute_value.attribute_id.id
        }
        return data

    def create_shopify_record(self, instance, attribute_value):
        """
        Created shopify data in layer model shopify to odoo
        :param instance: shopify Instance
        :param attribute_value: attribute value model domain
        :return:
        """
        data = self.ks_map_prepare_data_for_layer(instance, attribute_value)
        try:
            shopify_attribute_term = self.create(data)
            return shopify_attribute_term
        except Exception as e:
            self.env['ks.shopify.logger'].ks_create_prepare_log_params(operation_performed="prepare_create",
                                                                   status="failed",
                                                                   type="attribute_value",
                                                                   instance=instance,
                                                                   odoo_model="product.attribute.value",
                                                                   layer_model="ks.shopify.pro.attr.value",
                                                                   id=attribute_value.id,
                                                                   message=str(e))

    def update_shopify_record(self, instance, attribute_value):
        """
        Updates layer model record with attribute data from shopify
        :param instance: Shopify Instances
        :param attribute_value: attribute value model domain
        :return:
        """
        data = self.ks_map_prepare_data_for_layer(instance, attribute_value)
        try:
            product_attr_value_exist = self.check_if_already_prepared(instance, attribute_value)
            if product_attr_value_exist:
                product_attr_value_exist.write(data)
                return product_attr_value_exist
        except Exception as e:
            self.env['ks.shopify.logger'].ks_create_prepare_log_params(operation_performed="prepare_update",
                                                                   status="failed",
                                                                   type="attribute_value",
                                                                   instance=instance,
                                                                   odoo_model="product.attribute.value",
                                                                   layer_model="ks.shopify.pro.attr.value",
                                                                   id=attribute_value.id,
                                                                   message=str(e))

    def update_record_data_in_odoo(self):
        """
        Use: This will update the Layer record data to The Main Attribute linked to it
        :return:
        """
        for rec in self:
            try:
                json_data = rec.ks_pro_attr_value.ks_map_odoo_attribute_term_data_to_update(rec)
                rec.ks_pro_attr_value.write(json_data)
                rec.ks_need_update = False
            except Exception as e:
                self.env['ks.shopify.logger'].ks_create_log_param('update', 'attribute_value', rec.ks_shopify_instance,
                                                              rec.ks_attribute_id.id, 'Failed due to',
                                                              rec.ks_shopify_attribute_id, 'wl_to_odoo',
                                                              'failed', 'product.attribute.value',
                                                              'ks.shopify.pro.attr.value', e)

    def ks_populate_layer_update_to_odoo(self):
        """
        Use: This will check the No of instance in the main record if single record exist then it will update directly
        :return: None
        """
        self.ks_need_update = True
        if len(self.ks_shopify_instance) == 1:
            self.update_record_data_in_odoo()

    def check_if_already_prepared(self, instance, product_attr_value):
        """
        Checks if the records are already prepared or not
        :param instance: Shopify Instances
        :param product_attr_value: Product attribute value layer model domain
        :return: product_attr_value domain
        """
        product_attr_value_exist = self.search([('ks_shopify_instance', '=', instance.id),
                                                ('ks_pro_attr_value', '=', product_attr_value.id)], limit=1)
        return product_attr_value_exist

    # def ks_shopify_export_attribute_terms(self, attribute_id):
    #     """
    #     Use: This will export the selected new records from Odoo to Shopify and then store the response
    #     :attribute_id: Id of shopify attribute to be created
    #     :return: None
    #     """
    #     for record in self:
    #         try:
    #             shopify_instance = record.ks_shopify_instance
    #             json_data = record.ks_prepare_export_json_data()
    #             if shopify_instance and not record.ks_shopify_attribute_term_id:
    #                 attribute_term_data = self.ks_shopify_post_attribute_term(json_data, attribute_id, shopify_instance)
    #                 if attribute_term_data:
    #                     self.env['ks.shopify.connector.instance'].ks_shopify_update_the_response(attribute_term_data, record,
    #                                                                                      'ks_shopify_attribute_term_id',
    #                                                                                      )
    #                     record.ks_shopify_attribute_id = attribute_id
    #         except Exception as e:
    #             self.env['ks.shopify.logger'].ks_create_log_param('create', 'attribute_value', record.ks_shopify_instance.id,
    #                                                           record.ks_attribute_id.id, 'Failed due to',
    #                                                           record.ks_shopify_attribute_id, 'wl_to_shopify',
    #                                                           'failed', 'product.attribute.value',
    #                                                           'ks.shopify.pro.attr.value', e)

    # def ks_shopify_update_attribute_terms(self, attribute_id):
    #     """
    #     Use: This will update the selected records from Odoo to Shopify and then store the response
    #     :attribute_id: Id of shopify attribute to be created
    #     :return: None
    #     """
    #     for record in self:
    #         try:
    #             shopify_instance = record.ks_shopify_instance
    #             json_data = record.ks_prepare_export_json_data()
    #             if shopify_instance and record.ks_shopify_attribute_term_id:
    #                 attribute_term_data = self.ks_shopify_update_attribute_term(attribute_id,
    #                                                                         record.ks_shopify_attribute_term_id,json_data,
    #                                                                         shopify_instance)
    #                 if attribute_term_data:
    #                     self.env['ks.shopify.connector.instance'].ks_shopify_update_the_response(attribute_term_data, record,
    #                                                                                      'ks_shopify_attribute_term_id',
    #                                                                                                                                                                              )
    #                     record.ks_shopify_attribute_id = attribute_id
    #         except Exception as e:
    #             self.env['ks.shopify.logger'].ks_create_log_param('update', 'attribute_value', record.ks_shopify_instance.id,
    #                                                           record.ks_attribute_id.id, 'Failed due to',
    #                                                           record.ks_shopify_attribute_id, 'wl_to_shopify',
    #                                                           'failed', 'product.attribute.value',
    #                                                           'ks.shopify.pro.attr.value', e)

    # def ks_shopify_import_attribute_terms(self):
    #     """
    #     Imports and update the attributes terms from shopify to odoo
    #     :return:
    #     """
    #     for record in self:
    #         try:
    #             shopify_instance = record.ks_shopify_instance
    #             if shopify_instance and record.ks_shopify_attribute_term_id and record.ks_shopify_attribute_id:
    #                 attribute_term_data = self.ks_shopify_get_attribute_term(record.ks_shopify_attribute_id,
    #                                                                      record.ks_shopify_attribute_term_id, shopify_instance)
    #                 if attribute_term_data:
    #                     json_data = record.ks_prepare_import_json_data(attribute_term_data, record.ks_shopify_attribute_id)
    #                     record.write(json_data)
    #                     self.env['ks.shopify.connector.instance'].ks_shopify_update_the_response(attribute_term_data, record,
    #                                                                                      'ks_shopify_attribute_term_id',
    #                                                                                      )
    #                     record.ks_populate_layer_update_to_odoo()
    #         except Exception as e:
    #             self.env['ks.shopify.logger'].ks_create_log_param('update', 'attribute', record.ks_shopify_instance.id,
    #                                                           record.ks_attribute_id.id, 'Failed due to',
    #                                                           record.ks_shopify_attribute_id, 'shopify_to_odoo',
    #                                                           'failed', 'product.attribute.value',
    #                                                           'ks.shopify.pro.attr.value', e)

    # def ks_shopify_get_all_attribute_terms(self, instance_id, attribute_id):
    #     """
    #     Gets all the attribute value from shopify to odoo
    #     :param instance_id: Shopify Instance
    #     :param attribute_id: Id of attribute to fetch from shopify
    #     :return: json data response
    #     """
    #     multi_api_call = True
    #     per_page = 100
    #     page = 1
    #     all_retrieved_data = []
    #     try:
    #         shopify_api = instance_id.ks_shopify_api_authentication()
    #         while multi_api_call:
    #             attribute_term_response = shopify_api.get("products/attributes/%s/terms" % attribute_id,
    #                                                  params={'per_page': per_page, 'page': page})
    #             if attribute_term_response.status_code in [200, 201]:
    #                 all_retrieved_data.extend(attribute_term_response.json())
    #             else:
    #                 self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                                    status="failed",
    #                                                                    type="attribute_value",
    #                                                                    operation_flow="shopify_to_odoo",
    #                                                                    instance=instance_id,
    #                                                                    shopify_id=0,
    #                                                                    layer_model="ks.shopify.pro.attr.value",
    #                                                                    message=str(attribute_term_response.text))
    #             total_api_calls = attribute_term_response.headers._store.get('x-wp-totalpages')[1]
    #             remaining_api_calls = int(total_api_calls) - page
    #             if remaining_api_calls > 0:
    #                 page += 1
    #             else:
    #                 multi_api_call = False
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                            status="success",
    #                                                            type="attribute_value",
    #                                                            operation_flow="shopify_to_odoo",
    #                                                            instance=instance_id,
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.pro.attr.value",
    #                                                            message="Fetch of Customer successful")
    #         return all_retrieved_data
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                            status="failed",
    #                                                            type="attribute_value",
    #                                                            instance=instance_id,
    #                                                            operation_flow="shopify_to_odoo",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.pro.attr.value",
    #                                                            message=str(e))
    # def ks_shopify_get_attribute_term(self, attribute_id, attribute_val_id, instance_id):
    #     """
    #     Gets a single attribute value from shopify to odoo
    #     :param attribute_id: Id of shopify attribute
    #     :param attribute_val_id: Id of shopify attribute value
    #     :param instance_id: Shopify Instance
    #     :return: json data response
    #     """
    #     try:
    #         shopify_api = instance_id.ks_shopify_api_authentication()
    #         shopify_attribute_term_response = shopify_api.get(
    #             "products/attributes/%s/terms/%s" % (attribute_id, attribute_val_id))
    #         if shopify_attribute_term_response.status_code in [200, 201]:
    #             attribute_term_data = shopify_attribute_term_response.json()
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                                status="success",
    #                                                                type="attribute_value",
    #                                                                operation_flow="shopify_to_odoo",
    #                                                                instance=instance_id,
    #                                                                shopify_id=attribute_term_data.get("id"),
    #                                                                layer_model="ks.shopify.pro.attr.value",
    #                                                                message="Fetch of Attribute Value successful")
    #             return attribute_term_data
    #         else:
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                                status="failed",
    #                                                                type="attribute_value",
    #                                                                operation_flow="shopify_to_odoo",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.pro.attr.value",
    #                                                                message=str(shopify_attribute_term_response.text))
    #             return False
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                            status="failed",
    #                                                            type="attribute_value",
    #                                                            instance=instance_id,
    #                                                            operation_flow="shopify_to_odoo",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.pro.attr.value",
    #                                                            message=str(e))

    # def ks_shopify_post_attribute_term(self, data, attribute_id, instance_id):
    #     """
    #     Create an attribute value on shopify
    #     :param data: json data to create attribute values
    #     :param attribute_id: Id of attributes
    #     :param instance_id: Shopify Instances
    #     :return: json data response
    #     """
    #     try:
    #         shopify_api = instance_id.ks_shopify_api_authentication()
    #         shopify_attribute_term_response = shopify_api.post("products/attributes/%s/terms" % attribute_id, data)
    #         if shopify_attribute_term_response.status_code in [200, 201]:
    #             attribute_term_data = shopify_attribute_term_response.json()
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="create",
    #                                                                status="success",
    #                                                                type="attribute_value",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=attribute_term_data.get("id"),
    #                                                                layer_model="ks.shopify.pro.attr.value",
    #                                                                message="Create of Attribute Value successful")
    #             return attribute_term_data
    #         else:
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="create",
    #                                                                status="failed",
    #                                                                type="attribute_value",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.pro.attr.value",
    #                                                                message=str(shopify_attribute_term_response.text))
    #     except ConnectionError:
    #         raise Exception(
    #             "Couldn't Connect the Instance at time of attribute_value Syncing !! Please check the network "
    #             "connectivity or the configuration parameters are not correctly set")
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="create",
    #                                                            status="failed",
    #                                                            type="attribute_value",
    #                                                            instance=instance_id,
    #                                                            operation_flow="odoo_to_shopify",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.pro.attr.value",
    #                                                            message=str(e))

    # def ks_shopify_update_attribute_term(self, attribute_id, attribute_val_id, data, instance_id):
    #     """
    #     Update Attribute values on shopify
    #     :param attribute_id: Id of attribute to update
    #     :param attribute_val_id: Id of attribute value to update
    #     :param data: data to update attribute value
    #     :param instance_id: shopify instance
    #     :return: json data response
    #     """
    #     try:
    #         shopify_api = instance_id.ks_shopify_api_authentication()
    #         shopify_attribute_term_response = shopify_api.put(
    #             "products/attributes/%s/terms/%s" % (attribute_id, attribute_val_id),
    #             data)
    #         if shopify_attribute_term_response.status_code in [200, 201]:
    #             attribute_term_data = shopify_attribute_term_response.json()
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="update",
    #                                                                status="success",
    #                                                                type="attribute_value",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=attribute_term_data.get("id"),
    #                                                                layer_model="ks.shopify.pro.attr.value",
    #                                                                message="Update of Attribute Value successful")
    #             return attribute_term_data
    #         else:
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="update",
    #                                                                status="failed",
    #                                                                type="attribute_value",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.pro.attr.value",
    #                                                                message=str(shopify_attribute_term_response.text))
    #     except ConnectionError:
    #         raise Exception(
    #             "Couldn't Connect the Instance at time of attribute_value Syncing !! Please check the network "
    #             "connectivity or the configuration parameters are not correctly set")
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="update",
    #                                                            status="failed",
    #                                                            type="attribute_value",
    #                                                            instance=instance_id,
    #                                                            operation_flow="odoo_to_shopify",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.pro.attr.value",
    #                                                            message=str(e))

    def ks_prepare_import_json_data(self, json_data, attribute_id):
        """
        Prepares data to be imported on odoo from shopify
        :param json_data: api json data from shopify
        :param attribute_id: id of attribute
        :return: json data
        """
        data = {
            "ks_name": json_data.get('name'),
            # "ks_slug": json_data.get('slug') or '',
            "ks_shopify_attribute_id": attribute_id
        }
        return data

    def ks_manage_attribute_value_import(self, shopify_instance, shopify_attribute, odoo_attribute, queue_record=False):
        try:
            for value_data in shopify_attribute.get('values'):
                layer_attribute_value = self.search([('ks_shopify_instance', '=', shopify_instance.id),
                                                     ("ks_attribute_id", '=', odoo_attribute.id),
                                                     ("ks_name", '=', value_data)
                                                     ])
                odoo_attribute_value = layer_attribute_value.ks_pro_attr_value
                odoo_main_data = self.ks_map_attribute_value_data_for_odoo(value_data, odoo_attribute.id)
                if layer_attribute_value:
                    odoo_attribute_value.ks_manage_attribute_value_in_odoo(odoo_main_data.get('name'),
                                                                           odoo_attribute.id,
                                                                           odoo_attribute_value=odoo_attribute_value)
                    layer_data = self.ks_map_attribute_value_data_for_layer(value_data, odoo_attribute, odoo_attribute_value, shopify_attribute.get('id'), shopify_instance)
                    layer_attribute_value.write(layer_data)
                else:
                    odoo_attribute_value = odoo_attribute_value.ks_manage_attribute_value_in_odoo(odoo_main_data.get('name'),
                                                                                                  odoo_attribute.id,
                                                                                                  odoo_attribute_value=odoo_attribute_value)
                    layer_data = self.ks_map_attribute_value_data_for_layer(value_data,
                                                                            odoo_attribute,
                                                                            odoo_attribute_value, shopify_attribute.get('id'), shopify_instance)
                    layer_attribute_value = self.create(layer_data)
        except Exception as e:
            if queue_record:
                queue_record.ks_update_failed_state()
            _logger.info(str(e))

    def ks_map_attribute_value_data_for_odoo(self, value_data, attribute_id):
        data = {
            "name": value_data,
            "display_type": 'select',
            "attribute_id": attribute_id
        }
        return data

    def ks_prepare_export_json_data(self, odoo_attribute_value):
        """
        Prepares to export json data from odoo to shopify
        :return: shopify compatible data
        """
        data = {
            "name": odoo_attribute_value.name,
            # "slug": self.ks_slug if self.ks_slug else '',
        }
        return data
    
    def ks_manage_attribute_value_export(self, attribute_id, queue_record=False):
        """
        :param queue_record: Queue Boolean Trigger
        :return: json response
        """
        try:
            for attribute_value in self:
                odoo_base_attribute_value = attribute_value.ks_pro_attr_value
                shopify_attribute_id = attribute_value.ks_shopify_attribute_id or attribute_id
                shopify_attribute_value_id = attribute_value.ks_shopify_attribute_term_id
                shopify_attribute_data = attribute_value.ks_prepare_export_json_data(odoo_base_attribute_value)
                if shopify_attribute_value_id:
                    shopify_attribute_value_data_response = attribute_value.ks_shopify_update_attribute_term(shopify_attribute_id,
                                                                                          shopify_attribute_value_id,
                                                                                          shopify_attribute_data,
                                                                                          self.ks_shopify_instance)
                else:
                    shopify_attribute_value_data_response = attribute_value.ks_shopify_post_attribute_term(shopify_attribute_data,shopify_attribute_id,

                                                                                   self.ks_shopify_instance)
                if shopify_attribute_value_data_response:
                    self.env['ks.shopify.connector.instance'].ks_shopify_update_the_response(shopify_attribute_value_data_response,
                                                                                     attribute_value,
                                                                                     'ks_shopify_attribute_term_id',
                                                                                             {
                                                                                         "ks_shopify_attribute_id": shopify_attribute_id}
                                                                                     )
        except Exception as e:
            if queue_record:
                queue_record.ks_update_failed_state()

    def ks_map_attribute_value_data_for_layer(self, value_data, odoo_attribute, odoo_attribute_value, shopify_attribute_id, shopify_instance):
        data = {
                "ks_name": value_data,
                # "ks_slug": value_data.get('slug') or '',
                "ks_shopify_attribute_id": shopify_attribute_id,
                "ks_attribute_id": odoo_attribute.id,
                "ks_shopify_instance": shopify_instance.id,
                "ks_pro_attr_value": odoo_attribute_value.id,
                # "ks_shopify_attribute_term_id": value_data.get('id')

            }
        return data
