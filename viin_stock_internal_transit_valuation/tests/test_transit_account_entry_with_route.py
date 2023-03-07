from datetime import datetime, timedelta

from odoo.tests import tagged, Form, api
from .common import TestTransitTransferCommon


@tagged('-at_install', 'post_install')
class TestTransitTransferWithRoute(TestTransitTransferCommon):

    def _create_purchase_order(self, product, quantity, unit_cost):
        po = self.env['purchase.order'].create({
            'partner_id': self.env.ref('base.res_partner_address_4').id,
            'date_order': datetime.today() + timedelta(days=7),
            'order_line': [(0, 0, {
                'name': 'System 69',
                'product_id': product.id,
                'product_qty': quantity,
                'product_uom': self.env.ref('uom.product_uom_unit').id,
                'price_unit': unit_cost,
            })]
        })

        po.button_confirm()
        picking = po.picking_ids[0]
        res_dict = picking.button_validate()
        self.env[res_dict['res_model']].with_context(res_dict['context']).create({}).process()

    def test_10(self):
        '''
            Input:
                Warehouse
                    A sub warehouse, SWH, with resupply from the WH warehouse
                Route
                    Route for resupply:
                        . WH/stock -> transit location
                        . transit location -> sub warehouse
                        . where:
                            transit location has Accounts
                        . consists of 2 rules
                Rule:
                    1)
                        . pull rule
                        . make from stock
                        . from Wh/stock location
                        . to transit location
                    2)
                        . pull rule
                        . mfs_else_mfo
                        . from transit location
                        . to sub warehouse location
                Product 1
                    Type:            storagable
                    cost_method:     fifo
                    valuation:       automated
                    route_ids:       route for resupply
                Reordering Rule
                    Location:        sub-warehouse locatin
                    Min              2
                    Max              3
                    
            Process:
                1) Buy product 1 with quantity = 2 and cost = 10
                2) Buy product 1 with quantity = 2 and cost = 5
                3) Run Scheduler
            
            Expect:
                2 new stock.moves generated:
                    1 with 
                        status 'wait for another'
                        from WH/stock
                        to transit loc
                    1 with
                        status 'need confirm'
                        from transit loc
                        to SWH/stock
                SWH is stocked with 3 of product 1 and the valuation is
                    10 + 10 + 5 = 25
                
        '''
        # ------------------------ #
        # ---     WAREHOUSE    --- #
        # ------------------------ #
        sub_warehouse = self.env['stock.warehouse'].create({
            'name': 'My Sub Warehouse (San Francisco)',
            'code': 'SWH',
            'company_id': self.env.company.id,
        })
        sub_warehouse.resupply_wh_ids = [(6, 0, [self.env.ref('stock.warehouse0').id])]

        sub_warehouse_location = sub_warehouse.lot_stock_id

        # -------------------- #
        # ---     ROUTE    --- #
        # -------------------- #
        resupply_route = sub_warehouse.resupply_route_ids.filtered(
            lambda sr: sr.name == 'My Sub Warehouse (San Francisco): Supply Product from San Francisco'
        )

        # The resupply route has 2 rules
        #     1 from WH/stock to transit location
        #     1 from transit to SubWH/Stock location
        #
        # Update Accounts on the transit location
        route_rule_inter_to_transit = resupply_route.rule_ids.filtered(
            lambda r: r.location_src_id.id == self.wh_stock_internal_location.id
        )

        test_transit_location = route_rule_inter_to_transit.location_id
        test_transit_location.write({
            'valuation_in_account_id': self.stock_val_acc_in.id,
            'valuation_out_account_id': self.stock_val_acc_out.id,
        })

        # ---------------------- #
        # ---     PRODUCT    --- #
        # ---------------------- #
        self.salesable_prod_categ.write({
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time'
        })

        # We're gonna use "Run Scheduler" feature from Inventory module
        # to create 2 stock moves at the same times
        #
        # We create new product for avoiding complicatation on checking assert
        product_1 = self.env['product.product'].create({
            'name': 'Product to Test 1',
            'type': 'product',
            'categ_id': self.salesable_prod_categ.id,
            'route_ids': [(4, resupply_route.id)]
        })

        # ------------------------------ #
        # ---     REORDERING RULE    --- #
        # ------------------------------ #

        # Note:
        #    Value of 'warehouse_id' and 'route_id'
        #
        #    We dont have to enter these values when creating new orderpoint using Form
        #    But they are required on ORM for the logic to be able to find the corresponding reordering rules
        reordering_rule = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': sub_warehouse.id,
            'location_id': sub_warehouse.lot_stock_id.id,
            'product_min_qty': 2,
            'product_max_qty': 4,
            'qty_multiple': 1.0,
            'trigger': 'auto',
            'product_id': product_1.id,
            'route_id': resupply_route.id
        })

        # -------------------------------------------------- #
        # General check before moving on                     #
        # -------------------------------------------------- #

        # Resupply from WH
        self.assertEqual(sub_warehouse.resupply_wh_ids.ids, [self.env.ref('stock.warehouse0').id])
        self.assertTrue(sub_warehouse_location)

        self.assertEqual(
            resupply_route.name,
            'My Sub Warehouse (San Francisco): Supply Product from San Francisco',
        )
        self.assertRecordValues(resupply_route, [{
            'name': 'My Sub Warehouse (San Francisco): Supply Product from San Francisco',
            'product_categ_selectable': True,
            'product_selectable': True,
            'warehouse_selectable': True,
        }])
        self.assertEqual(len(resupply_route.rule_ids), 2)
        self.assertRecordValues(route_rule_inter_to_transit, [{
            'action': 'pull',
            'location_src_id': self.wh_stock_internal_location.id,
            'location_id': test_transit_location.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.env.ref('stock.warehouse0').id
        }])
        self.assertRecordValues(resupply_route.rule_ids[1], [{
            'action': 'pull',
            'location_src_id': test_transit_location.id,
            'location_id': sub_warehouse.lot_stock_id.id,
            'procure_method': 'make_to_order',
            'warehouse_id': sub_warehouse.id
        }])
        self.assertTrue(test_transit_location.valuation_in_account_id)
        self.assertTrue(test_transit_location.valuation_out_account_id)

        # -------------------------------------------------- #
        # Buy this product with price 10 and 5, respectively #
        # -------------------------------------------------- #

        self._create_purchase_order(product_1, 2, 10)
        self._create_purchase_order(product_1, 4, 8)

        self.assertEqual(len(product_1.stock_move_ids), 2)
        self.assertRecordValues(product_1.stock_move_ids, [
            {
                'product_id': product_1.id,
                'state': 'done',
                'location_dest_id': self.wh_stock_internal_location.id,
            },
            {
                'product_id': product_1.id,
                'state': 'done',
                'location_dest_id': self.wh_stock_internal_location.id,
            },
        ])

        self.assertRecordValues(product_1, [{
            'qty_available': 6,
            'purchased_product_qty': 6,
        }])

        # There are now 4 units of Product 1 stocking at WH/Stock
        stock_quant = product_1.stock_quant_ids.filtered(lambda sq: sq.value > 0)
        self.assertRecordValues(stock_quant, [{
            'location_id': self.wh_stock_internal_location.id,
            'available_quantity': 6,
        }])

        whstock_product_1_quant = self.wh_stock_internal_location.quant_ids.filtered(lambda q: q.product_id.id == product_1.id)
        sub_whstock_product_1_quant = sub_warehouse_location.quant_ids.filtered(lambda q: q.product_id.id == product_1.id)
        self.assertTrue(whstock_product_1_quant)
        self.assertFalse(sub_whstock_product_1_quant)

        # ----------------------- #
        # execute Run Scheduler   #
        # ----------------------- #
        self.env['procurement.group'].run_scheduler(company_id=self.env.company.id)

        # Retrieve the 2 stock pickings that are just following the reordering rule
        receipt_moves = self.env['stock.picking'].search([
            ('product_id', '=', product_1.id),
            '|',
                ('location_id', '=', test_transit_location.id),
                ('location_dest_id', '=', test_transit_location.id)
        ])

        self.assertEqual(len(receipt_moves), 2)

        picking_waiting = receipt_moves.filtered(lambda m: m.state == 'waiting')
        picking_assigned = receipt_moves - picking_waiting

        self.assertRecordValues(picking_waiting, [{
            'state': 'waiting',
            'location_id': test_transit_location.id,
            'location_dest_id': sub_warehouse_location.id,
        }])
        self.assertRecordValues(picking_assigned, [{
            'state': 'assigned',
            'location_id': self.wh_stock_internal_location.id,
            'location_dest_id': test_transit_location.id
        }])

        # Validate first stock picking
        first_result = picking_assigned.button_validate()
        self.env[first_result['res_model']].with_context(first_result['context']).create({}).process()

        self.assertEqual(picking_waiting.state, 'assigned')
        self.assertEqual(picking_assigned.state, 'done')

        # Validate second stock picking
        second_result = picking_waiting.button_validate()
        self.env[second_result['res_model']].with_context(second_result['context']).create({}).process()

        self.assertEqual(picking_waiting.state, 'done')
        self.assertEqual(picking_assigned.state, 'done')

        # We have transfered 3 of product 1 from WH/Stock to SWH/Stock
        self.assertEqual(picking_assigned.move_line_ids.qty_done, 4)
        self.assertEqual(picking_waiting.move_line_ids.qty_done, 4)

        # The cost of product should be 10 + 10 + 5 = 25
        self.assertEqual(picking_assigned.account_move_ids.amount_total, 36)
        self.assertEqual(picking_waiting.account_move_ids.amount_total, 36)

        # Account move lines of Picking Assigned
        pa_aml_from_wh = picking_assigned.account_move_line_ids.filtered(lambda aml: aml.balance < 0)
        pa_aml_to_transit = picking_assigned.account_move_line_ids - pa_aml_from_wh

        # Account move lines of Picking Waiting
        pw_aml_from_transit = picking_waiting.account_move_line_ids.filtered(lambda aml: aml.balance < 0)
        pw_aml_to_sub_wh = picking_waiting.account_move_line_ids - pw_aml_from_transit

        self.assertRecordValues(pa_aml_from_wh, [{'debit': 0, 'credit': 36, 'balance':-36}])
        self.assertRecordValues(pa_aml_to_transit, [{'debit': 36, 'credit': 0, 'balance': 36}])

        self.assertRecordValues(pw_aml_from_transit, [{'debit': 0, 'credit': 36, 'balance':-36}])
        self.assertRecordValues(pw_aml_to_sub_wh, [{'debit': 36, 'credit': 0, 'balance': 36}])
        
        self.assertEqual(product_1.standard_price, 8)

