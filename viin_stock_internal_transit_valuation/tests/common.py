from odoo.tests import SavepointCase, tagged


@tagged('-at_install', 'post_install')
class TestTransitTransferCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.account_stock_valuation = cls.env.ref('l10n_generic_coa.1_stock_valuation')
        cls.stock_val_acc_in = cls.env.ref('l10n_generic_coa.1_stock_in')
        cls.stock_val_acc_out = cls.env.ref('l10n_generic_coa.1_stock_out')
        cls.wh_stock_internal_location = cls.env.ref('stock.stock_location_stock')
        cls.order_processing_internal_location = cls.env.ref('stock.location_order')

        # ACTIVATE the features:
        #    Multi storage locations
        cls.env.user.write({
            'groups_id': [
                (4, cls.env.ref('stock.group_stock_multi_locations').id)
            ]
        })

        # Initially has neither company nor accounts
        cls.inter_company_transit_location = cls.env.ref('stock.stock_location_inter_wh')
        cls.inter_company_transit_location.write({'active': True})
        # Initially has company but no accounts
        cls.inter_warehouse_transit_location = cls.env.company.internal_transit_location_id
        cls.inter_warehouse_transit_location.write({
            'valuation_in_account_id': cls.stock_val_acc_in.id,
            'valuation_out_account_id': cls.stock_val_acc_out.id,
            'active': True,
        })

        # Initially, this category from the Demo data has:
        #    Costing Method:             Standard Price
        #    Inventory Valuation:        Manual               <------
        #    Stock Input Account:        110200 Stock Interim (Received)
        #    Stock Output Account:       110300 Stock Interim (Delivered)
        #    Stock Valuation Account:    110100 Stock Valuation
        cls.office_furniture_prod_categ = cls.env.ref('product.product_category_5')

        # Sales Price         $85.00
        # Cost                $78.00
        # Category            office furniture
        cls.furniture_product = cls.env.ref('product.product_product_13')

        # Initially, this category after modification has:
        #    Costing Method:             Standard Price
        #    Inventory Valuation:        Automated            <------
        #    Stock Input Account:        110200 Stock Interim (Received)
        #    Stock Output Account:       110300 Stock Interim (Delivered)
        #    Stock Valuation Account:    110100 Stock Valuation
        cls.salesable_prod_categ = cls.env.ref('product.product_category_1')
        cls.salesable_prod_categ.write({'property_valuation': 'real_time'})

        # Sales Price         $450.00
        # Cost                $300.00
        # Category            salesable
        cls.salesable_product = cls.env.ref('product.product_product_3')
        cls.salesable_product.write({'categ_id': cls.salesable_prod_categ.id})

    def _create_stock_picking_order(self, from_location, to_location, product_list, transfer_quantity=1):
        val = {
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'location_id': from_location.id,
            'location_dest_id': to_location.id,
            'scheduled_date': '2021-10-18 14:07:06',
        }

        if product_list:
            val['move_ids_without_package'] = []
            for product in product_list:
                move_id = (0, 0, {
                    'name': 'Stock Move Line 1',
                    'product_id': product.id,
                    'product_uom_qty': transfer_quantity,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                })
                val['move_ids_without_package'].append(move_id)

        # Create a stock picking order
        transfer_order = self.env['stock.picking'].with_context(tracking_disabled=True).create(val)
        transfer_order.action_confirm()
        transfer_order.action_assign()
        transfer_order.button_validate()

        # Record 'done' quantity
        SIT = self.env['stock.immediate.transfer']
        stock_immediate_transfer = SIT.with_context(default_show_transfers=False,
                                                    default_pick_ids=transfer_order.ids,
                                                    button_validate_picking_ids=transfer_order.ids).create({})
        stock_immediate_transfer.process()

        return transfer_order
