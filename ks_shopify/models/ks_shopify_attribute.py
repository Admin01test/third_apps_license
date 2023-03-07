# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class KsProductAttributeInherit(models.Model):
    _inherit = "product.attribute"

    ks_connected_shopify_attributes = fields.One2many('ks.shopify.product.attribute', 'ks_product_attribute',
                                                  string="Shopify Attribute Ids")

    def action_shopify_layer_attributes(self):
        """
        opens wizard fot shopify layer attributes
        :return: action
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("ks_shopify.action_ks_shopify_product_attribute")
        action['domain'] = [('id', 'in', self.ks_connected_shopify_attributes.ids)]
        return action

    # def ks_push_to_shopify(self):
    #     if self:
    #         instances = self.env['ks.shopify.connector.instance'].search([('ks_instance_state', 'in', ['active'])])
    #         if len(instances) > 1:
    #             action = self.env.ref('ks_shopify.ks_instance_selection_action_push').read()[0]
    #             action['context'] = {'push_to_shopify': True}
    #             return action
    #         else:
    #             data_prepared = self.ks_connected_shopify_attributes.filtered(lambda x: x.ks_shopify_instance.id == instances.id)
    #             if data_prepared:
    #                 ##Run update shopify record command here
    #                 self.env['ks.shopify.product.attribute'].update_shopify_record(instances, self, export_to_shopify=True)
    #             else:
    #                 self.env['ks.shopify.product.attribute'].create_shopify_record(instances, self, export_to_shopify=True)
    #     else:
    #         active_ids = self.env.context.get("active_ids")
    #         instances = self.env['ks.shopify.connector.instance'].search([('ks_instance_state', 'in', ['active'])])
    #         if len(instances) > 1:
    #             action = self.env.ref('ks_shopify.ks_instance_selection_action_push').read()[0]
    #             action['context'] = {'push_to_shopify': True, 'active_ids': active_ids, 'active_model': 'product.attribute'}
    #             return action
    #         else:
    #             records = self.browse(active_ids)
    #             if len(records) == 1:
    #                 data_prepared = records.ks_connected_shopify_attributes.filtered(
    #                     lambda x: x.ks_shopify_instance.id == instances.id)
    #                 if data_prepared:
    #                     ##Run update shopify record command here
    #                     self.env['ks.shopify.product.attribute'].update_shopify_record(instances, records, export_to_shopify=True)
    #                 else:
    #                     self.env['ks.shopify.product.attribute'].create_shopify_record(instances, records, export_to_shopify=True)
    #             else:
    #                 for rec in records:
    #                     data_prepared = rec.ks_connected_shopify_attributes.filtered(
    #                         lambda x: x.ks_shopify_instance.id == instances.id)
    #                     if data_prepared:
    #                         self.env['ks.shopify.queue.jobs'].ks_create_prepare_record_in_queue(instances,
    #                                                                                         'ks.shopify.product.attribute',
    #                                                                                         'product.attribute', rec.id,
    #                                                                                         'update', True, True)
    #                     else:
    #                         self.env['ks.shopify.queue.jobs'].ks_create_prepare_record_in_queue(instances,
    #                                                                                         'ks.shopify.product.attribute',
    #                                                                                         'product.attribute', rec.id,
    #                                                                                         'create', True, True)
    #
    # def ks_pull_from_shopify(self):
    #     if self:
    #         instance_counts = self.env['ks.shopify.connector.instance'].search([('ks_instance_state', 'in', ['active'])])
    #         if len(instance_counts) > 1:
    #             action = self.env.ref('ks_shopify.ks_instance_selection_action_pull').read()[0]
    #             action['context'] = {'pull_from_shopify': True}
    #             return action
    #         else:
    #             data_prepared = self.ks_connected_shopify_attributes.filtered(
    #                 lambda x: x.ks_shopify_instance.id == instance_counts.id)
    #             if data_prepared and data_prepared.ks_shopify_attribute_id:
    #                 ##Handle shopify import here
    #                 shopify_id = data_prepared.ks_shopify_attribute_id
    #                 json_data = self.env['ks.shopify.product.attribute'].ks_shopify_get_attribute(shopify_id, instance_counts)
    #                 if json_data:
    #                     attributes = self.env['ks.shopify.product.attribute'].ks_manage_attribute_import(instance_counts,
    #                                                                                                  json_data)
    #                 else:
    #                     _logger.info("Fatal Error in Syncing Attributes and its values from shopify")
    #
    #             else:
    #                 _logger.info("Layer record must have shopify id")
    #     else:
    #         active_ids = self.env.context.get("active_ids")
    #         instances = self.env['ks.shopify.connector.instance'].search([('ks_instance_state', 'in', ['active'])])
    #         if len(instances) > 1:
    #             action = self.env.ref('ks_shopify.ks_instance_selection_action_pull').read()[0]
    #             action['context'] = {'pull_from_shopify': True, 'active_ids': active_ids,
    #                                  'active_model': 'product.attribute'}
    #             return action
    #         else:
    #             records = self.browse(active_ids)
    #             if len(records) == 1:
    #                 data_prepared = records.ks_connected_shopify_attributes.filtered(
    #                     lambda x: x.ks_shopify_instance.id == instances.id)
    #                 if data_prepared and data_prepared.ks_shopify_attribute_id:
    #                     ##Handle shopify import here
    #                     shopify_id = data_prepared.ks_shopify_attribute_id
    #                     json_data = self.env['ks.shopify.product.attribute'].ks_shopify_get_attribute(shopify_id, instances)
    #                     if json_data:
    #                         attributes = self.env['ks.shopify.product.attribute'].ks_manage_attribute_import(instances,
    #                                                                                                      json_data)
    #                     else:
    #                         _logger.info("Fatal Error in Syncing Attributes and its values from shopify")
    #             else:
    #                 for rec in records:
    #                     data_prepared = rec.ks_connected_shopify_attributes.filtered(
    #                         lambda x: x.ks_shopify_instance.id == instances.id)
    #                     shopify_id = data_prepared.ks_shopify_attribute_id
    #                     json_data = self.env['ks.shopify.product.attribute'].ks_shopify_get_attribute(shopify_id, instances)
    #                     if json_data:
    #                         self.env['ks.shopify.queue.jobs'].ks_create_attribute_record_in_queue(
    #                             instance=instances,
    #                             data=[json_data])

    # def ks_manage_direct_syncing(self, record, instance_ids, push=False, pull=False):
    #     try:
    #         if len(record) == 1:
    #             for instance in instance_ids:
    #                 if push:
    #                     data_prepared = record.ks_connected_shopify_attributes.filtered(
    #                         lambda x: x.ks_shopify_instance.id == instance.id)
    #                     if data_prepared:
    #                         ##Run update shopify record command here
    #                         self.env['ks.shopify.product.attribute'].update_shopify_record(instance, record, export_to_shopify=True)
    #                     else:
    #                         self.env['ks.shopify.product.attribute'].create_shopify_record(instance, record, export_to_shopify=True)
    #
    #                 elif pull:
    #                     ##Handling of pull ther records from shopify here
    #                     data_prepared = record.ks_connected_shopify_attributes.filtered(
    #                         lambda x: x.ks_shopify_instance.id == instance.id)
    #                     if data_prepared and data_prepared.ks_shopify_attribute_id:
    #                         ##Handle shopify import here
    #                         shopify_id = data_prepared.ks_shopify_attribute_id
    #                         json_data = self.env['ks.shopify.product.attribute'].ks_shopify_get_attribute(shopify_id, instance)
    #                         if json_data:
    #                             category = self.env['ks.shopify.product.attribute'].ks_manage_attribute_import(instance,
    #                                                                                                        json_data)
    #                         else:
    #                             _logger.info("Fatal Error in Syncing Attributes and its values from shopify")
    #
    #                     else:
    #                         _logger.info("Layer record must have shopify id")
    #         else:
    #             for instance in instance_ids:
    #                 if push:
    #                     for rec in record:
    #                         data_prepared = rec.ks_connected_shopify_attributes.filtered(
    #                             lambda x: x.ks_shopify_instance.id == instance.id)
    #                         if data_prepared:
    #                             self.env['ks.shopify.queue.jobs'].ks_create_prepare_record_in_queue(instance,
    #                                                                                             'ks.shopify.product.attribute',
    #                                                                                             'product.attribute',
    #                                                                                             rec.id,
    #                                                                                             'update', True, True)
    #                         else:
    #                             self.env['ks.shopify.queue.jobs'].ks_create_prepare_record_in_queue(instance,
    #                                                                                             'ks.shopify.product.attribute',
    #                                                                                             'product.attribute',
    #                                                                                             rec.id,
    #                                                                                             'create', True, True)
    #                 elif pull:
    #                     for rec in record:
    #                         data_prepared = rec.ks_connected_shopify_attributes.filtered(
    #                             lambda x: x.ks_shopify_instance.id == instance.id)
    #                         shopify_id = data_prepared.ks_shopify_attribute_id
    #                         json_data = self.env['ks.shopify.product.attribute'].ks_shopify_get_attribute(shopify_id, instance)
    #                         if json_data:
    #                             self.env['ks.shopify.queue.jobs'].ks_create_attribute_record_in_queue(
    #                                 instance=instance,
    #                                 data=[json_data])
    #
    #
    #     except Exception as e:
    #         _logger.info(str(e))

    # def open_mapper(self):
    #     """
    #     Open mapping wizard
    #     :return: mapped
    #     """
    #     active_records = self._context.get("active_ids", False)
    #     model = self.env['ir.model'].search([('model', '=', self._name)])
    #     mapped = self.env['ks.global.record.mapping'].action_open_attribute_mapping_wizard(model,
    #                                                                                        active_records,
    #                                                                                        "Attribute Record Mapping")
    #     return mapped

class KsModelProductAttribute(models.Model):
    _name = 'ks.shopify.product.attribute'
    _description = "Shopify Product Attribute"
    _rec_name = 'ks_name'

    # Fields need to be Connected to any Connector
    ks_shopify_instance = fields.Many2one("ks.shopify.connector.instance", string="Instance", readonly=True,
                                     help=_("Shopify Connector Instance reference"),
                                     ondelete='cascade')
    ks_shopify_attribute_id = fields.Char('Shopify Attribute ID', readonly=True,
                                         help=_("the record id of the attribute record defined in the Connector"))
    ks_product_attribute = fields.Many2one('product.attribute', string="Odoo Product Attribute", readonly=True,
                                           ondelete='cascade', help="Displays Odoo Product Attribute Reference")
    ks_need_update = fields.Boolean(help=_("This will need to determine if a record needs to be updated, Once user "
                                           "update the record it will set as False"), readonly=True,
                                    string="Need Update")
    ks_mapped = fields.Boolean(string="Manual Mapping", readonly = True)

    # Connector Information related
    ks_name = fields.Char(string="Name", related='ks_product_attribute.name', help="Displays Shopify Attribute Name")
    ks_slug = fields.Char(string="Slug", help="Displays Shopify Attribute Slug Name")
    ks_display_type = fields.Selection([
        ('radio', 'Radio'),
        ('select', 'Select'),
        ('color', 'Color')], default='radio', string="Type", required=True,
        help="The display type used in the Product Configurator.")

    def check_if_already_prepared(self, instance, product_attribute):
        """
        Checks if data is already prepared for exporting on layer model
        :param instance: shopify instance
        :param product_attribute: shopify product attribute
        :return: attribute_exist
        """
        attribute_exist = self.search([('ks_shopify_instance', '=', instance.id),
                                       ('ks_product_attribute', '=', product_attribute.id)], limit=1)
        if attribute_exist:
            return attribute_exist
        else:
            return False

    # def ks_action_sync_attributes_from_shopify(self):
    #     if len(self) > 1:
    #         try:
    #             records = self.filtered(lambda e: e.ks_shopify_attribute_id and e.ks_shopify_instance)
    #             for i in records:
    #                 json_data = [self.ks_shopify_get_attribute(i.ks_shopify_attribute_id, i.ks_shopify_instance)]
    #                 if json_data[0]:
    #                     self.env['ks.shopify.queue.jobs'].ks_create_attribute_record_in_queue(data=json_data,
    #                                                                                       instance=i.ks_shopify_instance)
    #             return self.env['ks.message.wizard'].ks_pop_up_message("Success",
    #                                                                    '''Attributes Enqueued, Please refer Logs and Queues
    #                                                                    for further Details.''')
    #         except Exception as e:
    #             raise e
    #
        # else:
        #     try:
        #         self.ensure_one()
        #         if self.ks_shopify_attribute_id:
        #             data = self.ks_shopify_get_attribute(self.ks_shopify_attribute_id, self.ks_shopify_instance)
        #             attribute = self.ks_manage_attribute_import(self.ks_shopify_instance, data)
        #             self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="update",
        #                                                                ks_model='product.attribute',
        #                                                                ks_layer_model='ks.shopify.product.attribute',
        #                                                                ks_message="Attribute sync from shopify successi",
        #                                                                ks_status="success",
        #                                                                ks_type="attribute",
        #                                                                ks_record_id=attribute.id,
        #                                                                ks_operation_flow="shopify_to_odoo",
        #                                                                ks_shopify_id=data.get("id", 0) if data else 0,
        #                                                                ks_shopify_instance=self.ks_shopify_instance)
        #
        #     except Exception as e:
        #         self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="update",
        #                                                            ks_model='product.attribute',
        #                                                            ks_layer_model='ks.shopify.product.attribute',
        #                                                            ks_message=str(e),
        #                                                            ks_status="failed",
        #                                                            ks_type="attribute",
        #                                                            ks_record_id=0,
        #                                                            ks_operation_flow="shopify_to_odoo",
        #                                                            ks_shopify_id=0,
        #                                                            ks_shopify_instance=self.ks_shopify_instance)

    # def ks_action_sync_attributes_to_shopify(self):
    #     if len(self) > 1:
    #         try:
    #             records = self.filtered(lambda e: e.ks_shopify_instance)
    #             if len(records) > 0:
    #                 self.env['ks.shopify.queue.jobs'].ks_create_attribute_record_in_queue(records=records)
    #                 return self.env['ks.message.wizard'].ks_pop_up_message("Success",
    #                                                                        '''Attributes Enqueued, Please refer Logs and Queues for
    #                                                                        further Details.''')
    #         except Exception as e:
    #             raise e
    #
    #     else:
    #         self.ensure_one()
    #         try:
    #             shopify_attrib_response = self.ks_manage_attribute_export()
    #         except Exception as e:
    #             raise e

    def action_shopify_layer_attribute_terms(self):
        """
        opens layer model attributes values
        :return: action
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("ks_shopify.action_ks_shopify_product_attribute_value")
        action['domain'] = [('ks_attribute_id', '=', self.ks_product_attribute.id)]
        return action

    def ks_map_attribute_data_for_odoo(self, json_data):
        data = {}
        if json_data:
            data = {
                "name": json_data.get('name'),
                "display_type": 'select',
            }
        return data

    def ks_map_attribute_data_for_layer(self, attribute_data, product_attribute, instance):
        data = {
            "ks_product_attribute": product_attribute.id,
            "ks_shopify_instance": instance.id,
            "ks_display_type": "select",
            "ks_shopify_attribute_id": attribute_data.get("id")
        }
        return data

    def ks_manage_attribute_import(self, shopify_instance, attribute_data, queue_record=False):
        """
        :param shopify_instance:
        :param attribute_data: attributes json data
        :param queue_record: boolean trigger for queue
        :return: None
        """
        try:
            layer_attribute = self
            layer_attribute = self.search([('ks_shopify_instance', '=', shopify_instance.id),
                                           ("ks_shopify_attribute_id", '=', attribute_data.get("id") if attribute_data else None)])
            odoo_attribute = layer_attribute.ks_product_attribute
            odoo_main_data = self.ks_map_attribute_data_for_odoo(attribute_data)
            if layer_attribute:
                try:
                    odoo_attribute.ks_manage_attribute_in_odoo(odoo_main_data.get('name'),
                                                               odoo_main_data.get('display_type'),
                                                               odoo_attribute=odoo_attribute)
                    layer_data = self.ks_map_attribute_data_for_layer(attribute_data, odoo_attribute, shopify_instance)
                    layer_attribute.write(layer_data)
                    # attribute_terms = self.env['ks.shopify.pro.attr.value'].ks_shopify_get_all_attribute_terms(shopify_instance,
                    #                                                                                    layer_attribute.ks_shopify_attribute_id)
                    # if attribute_terms:
                    self.env['ks.shopify.pro.attr.value'].ks_manage_attribute_value_import(shopify_instance,
                                                                                       attribute_data,
                                                                                       odoo_attribute,
                                                                                       queue_record=queue_record)
                    self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="update",
                                                                       ks_model='product.attribute',
                                                                       ks_layer_model='ks.shopify.product.attribute',
                                                                       ks_message="Attribute import update success",
                                                                       ks_status="success",
                                                                       ks_type="attribute",
                                                                       ks_record_id=layer_attribute.id,
                                                                       ks_operation_flow="shopify_to_odoo",
                                                                       ks_shopify_id=attribute_data.get("id", 0),
                                                                       ks_shopify_instance=shopify_instance)
                except Exception as e:
                    self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="update",
                                                                       ks_model='product.attribute',
                                                                       ks_layer_model='ks.shopify.product.attribute',
                                                                       ks_message=str(e),
                                                                       ks_status="failed",
                                                                       ks_type="attribute",
                                                                       ks_record_id=layer_attribute.id,
                                                                       ks_operation_flow="shopify_to_odoo",
                                                                       ks_shopify_id=attribute_data.get("id", 0),
                                                                       ks_shopify_instance=shopify_instance)
            else:
                try:
                    if attribute_data.get('id'):
                        odoo_attribute = odoo_attribute.ks_manage_attribute_in_odoo(odoo_main_data.get('name'),
                                                                                    odoo_main_data.get('display_type'),
                                                                                    odoo_attribute=odoo_attribute)
                        layer_data = self.ks_map_attribute_data_for_layer(attribute_data, odoo_attribute, shopify_instance)
                        layer_attribute = self.create(layer_data)
                        # attribute_terms = self.env['ks.shopify.pro.attr.value'].ks_shopify_get_all_attribute_terms(shopify_instance,
                        #                                                                                    layer_attribute.ks_shopify_attribute_id)
                        # if attribute_terms:
                        self.env['ks.shopify.pro.attr.value'].ks_manage_attribute_value_import(shopify_instance,
                                                                                           attribute_data,
                                                                                           odoo_attribute,
                                                                                           queue_record=queue_record)
                        self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="create",
                                                                           ks_model='product.attribute',
                                                                           ks_layer_model='ks.shopify.product.attribute',
                                                                           ks_message="Attribute import create success",
                                                                           ks_status="success",
                                                                           ks_type="attribute",
                                                                           ks_record_id=layer_attribute.id,
                                                                           ks_operation_flow="shopify_to_odoo",
                                                                           ks_shopify_id=attribute_data.get("id", 0),
                                                                           ks_shopify_instance=shopify_instance)
                    else:
                        odoo_attribute = odoo_attribute.ks_manage_attribute_in_odoo(odoo_main_data.get('name'),
                                                                                    odoo_main_data.get(
                                                                                        'display_type'),
                                                                                    odoo_attribute=odoo_attribute)
                        # layer_data = self.ks_map_attribute_data_for_layer(attribute_data, odoo_attribute, shopify_instance)
                        # layer_attribute = self.create(layer_data)
                        # attribute_terms = self.env['ks.shopify.pro.attr.value'].ks_shopify_get_all_attribute_terms(shopify_instance,
                        #                                                                                    layer_attribute.ks_shopify_attribute_id)
                        # if attribute_terms:
                        #     self.env['ks.shopify.pro.attr.value'].ks_manage_attribute_value_import(shopify_instance,
                        #                                                                        attribute_data.get("id"),
                        #                                                                        odoo_attribute,
                        #                                                                        attribute_terms,
                        #                                                                        queue_record=queue_record)
                        for rec in attribute_data.get('options'):
                            data = {
                                "name": rec,
                                "display_type": 'select',
                                "attribute_id": odoo_attribute.id,
                            }
                            self.env['product.attribute.value'].ks_manage_attribute_value_in_odoo(data.get('name'),
                                                              odoo_attribute.id,
                                                              odoo_attribute_value=False)
                        self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="create",
                                                                           ks_model='product.attribute',
                                                                           ks_layer_model='ks.shopify.product.attribute',
                                                                           ks_message="Attribute import create success",
                                                                           ks_status="success",
                                                                           ks_type="attribute",
                                                                           ks_record_id=layer_attribute.id,
                                                                           ks_operation_flow="shopify_to_odoo",
                                                                           ks_shopify_id=attribute_data.get("id", 0),
                                                                           ks_shopify_instance=shopify_instance)
                except Exception as e:
                    self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="create",
                                                                       ks_model='product.attribute',
                                                                       ks_layer_model='ks.shopify.product.attribute',
                                                                       ks_message=str(e),
                                                                       ks_status="failed",
                                                                       ks_type="attribute",
                                                                       ks_record_id=0,
                                                                       ks_operation_flow="shopify_to_odoo",
                                                                       ks_shopify_id=attribute_data.get("id", 0),
                                                                       ks_shopify_instance=shopify_instance)
            return odoo_attribute
        except Exception as e:
            if queue_record:
                queue_record.ks_update_failed_state()
            raise e

    # def ks_prepare_export_json_data(self, odoo_attribute, layer_attribute):
    #     """
    #     prepares to export data to shopify
    #     :return: data
    #     """
    #     data = {
    #         "name": odoo_attribute.name,
    #         "slug": layer_attribute.ks_slug if layer_attribute.ks_slug else '',
    #         "type": 'select'
    #     }
    #     return data

    def ks_manage_attribute_export(self, queue_record=False):
        """
        :param queue_record: Queue Boolean Trigger
        :return: json response
        """
        shopify_attribute_data_response = None
        odoo_base_attribute = self.ks_product_attribute
        try:
            shopify_attribute_id = self.ks_shopify_attribute_id
            shopify_attribute_data = self.ks_prepare_export_json_data(odoo_base_attribute, self)
            if shopify_attribute_id:
                try:
                    shopify_attribute_data_response = self.ks_shopify_update_attribute(shopify_attribute_id, shopify_attribute_data,
                                                                               self.ks_shopify_instance)
                    self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="update",
                                                                       ks_model='product.attribute',
                                                                       ks_layer_model='ks.shopify.product.attribute',
                                                                       ks_message="Attribute Export Update Successful",
                                                                       ks_status="success",
                                                                       ks_type="attribute",
                                                                       ks_record_id=self.id,
                                                                       ks_operation_flow="odoo_to_shopify",
                                                                       ks_shopify_id=shopify_attribute_data_response.get("id",
                                                                                                                 0),
                                                                       ks_shopify_instance=self.ks_shopify_instance)
                except Exception as e:
                    self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="update",
                                                                       ks_model='product.attribute',
                                                                       ks_layer_model='ks.shopify.product.attribute',
                                                                       ks_message=str(e),
                                                                       ks_status="failed",
                                                                       ks_type="attribute",
                                                                       ks_record_id=self.id,
                                                                       ks_operation_flow="odoo_to_shopify",
                                                                       ks_shopify_id=0,
                                                                       ks_shopify_instance=self.ks_shopify_instance)
            else:
                try:
                    shopify_attribute_data_response = self.ks_shopify_post_attribute(shopify_attribute_data,
                                                                             self.ks_shopify_instance)
                    self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="create",
                                                                       ks_model='product.attribute',
                                                                       ks_layer_model='ks.shopify.product.attribute',
                                                                       ks_message="Attribute Export create Successful",
                                                                       ks_status="success",
                                                                       ks_type="attribute",
                                                                       ks_record_id=self.id,
                                                                       ks_operation_flow="odoo_to_shopify",
                                                                       ks_shopify_id=shopify_attribute_data_response.get("id",
                                                                                                                 0),
                                                                       ks_shopify_instance=self.ks_shopify_instance)
                except Exception as e:
                    self.env['ks.shopify.logger'].ks_create_odoo_log_param(ks_operation_performed="create",
                                                                       ks_model='product.attribute',
                                                                       ks_layer_model='ks.shopify.product.attribute',
                                                                       ks_message=str(e),
                                                                       ks_status="failed",
                                                                       ks_type="attribute",
                                                                       ks_record_id=self.id,
                                                                       ks_operation_flow="odoo_to_shopify",
                                                                       ks_shopify_id=0,
                                                                       ks_shopify_instance=self.ks_shopify_instance)
            if shopify_attribute_data_response:
                self.env['ks.shopify.connector.instance'].ks_shopify_update_the_response(shopify_attribute_data_response,
                                                                                 self,
                                                                                 'ks_shopify_attribute_id',
                                                                                 {
                                                                                     "ks_slug": shopify_attribute_data_response.get(
                                                                                         'slug') or ''}
                                                                                 )
            all_attribute_values = self.env['ks.shopify.pro.attr.value'].search(
                [('ks_attribute_id', '=', self.ks_product_attribute.id),
                 ('ks_shopify_instance', '=', self.ks_shopify_instance.id)])
            all_attribute_values.ks_manage_attribute_value_export(self.ks_shopify_attribute_id, queue_record)
            return shopify_attribute_data_response
        except Exception as e:
            if queue_record:
                queue_record.ks_update_failed_state()
            raise e

    def ks_map_prepare_data_for_layer(self, instance, product_attribute):
        """
        :param product_category: product.category()
        :param instance: ks.shopify.connector.instance()
        :return: layer compatible data
        """
        data = {
            "ks_product_attribute": product_attribute.id,
            "ks_shopify_instance": instance.id,
        }
        return data

    def create_shopify_record(self, instance, odoo_attribute, export_to_shopify=False, queue_record=False):
        """
        """
        try:
            shopify_layer_exist = self.search([("ks_product_attribute", '=', odoo_attribute.id),
                                           ('ks_shopify_instance', '=', instance.id)], limit=1)
            if not shopify_layer_exist:
                data = self.ks_map_prepare_data_for_layer(instance, odoo_attribute)
                layer_attribute = self.create(data)
                self.env['ks.shopify.pro.attr.value'].ks_manage_value_preparation(instance, odoo_attribute.value_ids)
                self.env['ks.shopify.logger'].ks_create_prepare_log_params(operation_performed="prepare_create",
                                                                       status="success",
                                                                       type="attribute",
                                                                       instance=instance,
                                                                       odoo_model="product.attribute",
                                                                       layer_model="ks.shopify.product.attribute",
                                                                       id=odoo_attribute.id,
                                                                       message="Layer preparation Success")
                if export_to_shopify:
                    try:
                        layer_attribute.ks_manage_attribute_export()
                    except Exception as e:
                        _logger.info(str(e))
                return layer_attribute
        except Exception as e:
            if queue_record:
                queue_record.ks_update_failed_state()
            self.env['ks.shopify.logger'].ks_create_prepare_log_params(operation_performed="prepare_create",
                                                                   status="failed",
                                                                   type="attribute",
                                                                   instance=instance,
                                                                   odoo_model="product.attribute",
                                                                   layer_model="ks.shopify.product.attribute",
                                                                   id=odoo_attribute.id,
                                                                   message=str(e))

    def update_shopify_record(self, instance, odoo_attribute, export_to_shopify=False, queue_record=False):
        """
        """
        try:
            shopify_layer_exist = self.search([("ks_product_attribute", '=', odoo_attribute.id),
                                           ('ks_shopify_instance', '=', instance.id)], limit=1)
            if shopify_layer_exist:
                data = self.ks_map_prepare_data_for_layer(instance, odoo_attribute)
                shopify_layer_exist.write(data)
                self.env['ks.shopify.pro.attr.value'].ks_manage_value_preparation(instance, odoo_attribute.value_ids)
                self.env['ks.shopify.logger'].ks_create_prepare_log_params(operation_performed="prepare_update",
                                                                       status="success",
                                                                       type="attribute",
                                                                       instance=instance,
                                                                       odoo_model="product.attribute",
                                                                       layer_model="ks.shopify.product.attribute",
                                                                       id=odoo_attribute.id,
                                                                       message="Layer preparation Success")
                if export_to_shopify:
                    try:
                        shopify_layer_exist.ks_manage_attribute_export()
                    except Exception as e:
                        _logger.info(str(e))
                return shopify_layer_exist
        except Exception as e:
            if queue_record:
                queue_record.ks_update_failed_state()
            self.env['ks.shopify.logger'].ks_create_prepare_log_params(operation_performed="prepare_update",
                                                                   status="failed",
                                                                   type="attribute",
                                                                   instance=instance,
                                                                   odoo_model="product.attribute",
                                                                   layer_model="ks.shopify.product.attribute",
                                                                   id=odoo_attribute.id,
                                                                   message=str(e))

    # def ks_shopify_get_all_attributes(self, instance_id):
    #     """
    #     Get all the attributes from api
    #     :param instance_id:
    #     :return: json data response
    #     """
    #     shopify_api = instance_id.ks_shopify_api_authentication()
    #     try:
    #         shopify_attribute_response = shopify_api.get("products/attributes")
    #         if shopify_attribute_response.status_code in [200, 201]:
    #             all_retrieved_data = shopify_attribute_response.json()
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                                status="success",
    #                                                                type="attribute",
    #                                                                operation_flow="shopify_to_odoo",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message="Fetch of attribute successful")
    #         else:
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                                status="failed",
    #                                                                type="attribute",
    #                                                                operation_flow="shopify_to_odoo",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message=str(shopify_attribute_response.text))
    #         return all_retrieved_data
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                            status="failed",
    #                                                            type="attribute",
    #                                                            instance=instance_id,
    #                                                            operation_flow="shopify_to_odoo",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.product.attribute",
    #                                                            message=str(e))

    # def ks_shopify_get_attribute(self, attribute_id, instance_id):
    #     """
    #     get specific attribute from api
    #     :param attribute_id: id of attribute
    #     :param instance_id: shopify instance
    #     :return: json response
    #     """
    #     try:
    #         shopify_api = instance_id.ks_shopify_api_authentication()
    #         shopify_attribute_response = shopify_api.get("products/attributes/%s" % (attribute_id))
    #         if shopify_attribute_response.status_code in [200, 201]:
    #             attribute_data = shopify_attribute_response.json()
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                                status="success",
    #                                                                type="attribute",
    #                                                                operation_flow="shopify_to_odoo",
    #                                                                instance=instance_id,
    #                                                                shopify_id=shopify_attribute_response.json().get("id"),
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message="Fetch of attribute successful")
    #             return attribute_data
    #         else:
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                                status="failed",
    #                                                                type="attribute",
    #                                                                operation_flow="shopify_to_odoo",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message=str(shopify_attribute_response.text))
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="fetch",
    #                                                            status="failed",
    #                                                            type="attribute",
    #                                                            instance=instance_id,
    #                                                            operation_flow="shopify_to_odoo",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.product.attribute",
    #                                                            message=str(e))

    # def ks_shopify_post_attribute(self, data, instance_id):
    #     """
    #     Create attribute on shopify through api
    #     :param data: data for attribute
    #     :param instance_id: shopify instance()
    #     :return: json response
    #     """
    #     try:
    #         shopify_api = instance_id.ks_shopify_api_authentication()
    #         shopify_attribute_response = shopify_api.post("products/attributes", data)
    #         if shopify_attribute_response.status_code in [200, 201]:
    #             attribute_data = shopify_attribute_response.json()
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="create",
    #                                                                status="success",
    #                                                                type="attribute",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=attribute_data.get("id"),
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message="Create of attribute successful")
    #             return attribute_data
    #         else:
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="create",
    #                                                                status="failed",
    #                                                                type="attribute",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message=str(shopify_attribute_response.text))
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="create",
    #                                                            status="failed",
    #                                                            type="attribute",
    #                                                            instance=instance_id,
    #                                                            operation_flow="odoo_to_shopify",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.product.attribute",
    #                                                            message=str(e))

    # def ks_shopify_update_attribute(self, attribute_id, data, instance_id):
    #     """
    #     :param attribute_id: shopify attribute id
    #     :param data: shopify compatible data
    #     :param instance_id: ks.shopify.connector.instance()
    #     :return: shopify json response
    #     """
    #     try:
    #         shopify_api = instance_id.ks_shopify_api_authentication()
    #         shopify_attribute_response = shopify_api.put("products/attributes/%s" % (attribute_id),
    #                                             data)
    #         if shopify_attribute_response.status_code in [200, 201]:
    #             attribute_data = shopify_attribute_response.json()
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="update",
    #                                                                status="success",
    #                                                                type="attribute",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=attribute_data.get("id"),
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message="Update of attribute successful")
    #             return attribute_data
    #         else:
    #             self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="update",
    #                                                                status="failed",
    #                                                                type="attribute",
    #                                                                operation_flow="odoo_to_shopify",
    #                                                                instance=instance_id,
    #                                                                shopify_id=0,
    #                                                                layer_model="ks.shopify.product.attribute",
    #                                                                message=str(shopify_attribute_response.text))
    #     except Exception as e:
    #         self.env['ks.shopify.logger'].ks_create_api_log_params(operation_performed="update",
    #                                                            status="failed",
    #                                                            type="attribute",
    #                                                            instance=instance_id,
    #                                                            operation_flow="odoo_to_shopify",
    #                                                            shopify_id=0,
    #                                                            layer_model="ks.shopify.product.attribute",
    #                                                            message=str(e))
