from odoo.tests import tagged, Form
from .common import TestTransitTransferCommon


@tagged('-at_install', 'post_install')
class TestTransitTransfer(TestTransitTransferCommon):

    def test_00_test_onchange(self):
        """
            Test onchange
            Expect:
                User can take action on 2 fields:
                    location_id
                    location_dest_id
        """
        with Form(self.env['stock.picking']) as transfer_order_form:
            transfer_order_form.picking_type_id = self.env.ref('stock.picking_type_internal')

            # Test if these 2 fields are not invisible after Internal Transfers operation type is selected
            self.assertFalse(transfer_order_form._get_modifier('location_id', 'invisible'))
            self.assertFalse(transfer_order_form._get_modifier('location_dest_id', 'invisible'))

    def test_01_transfer_no_transit_location(self):
        """
            Input:
                Operation Type = Internal Transfers
                FROM Internal location TO Internal location
            Expect:
                No stock valuation generated
                No journal entry generated
        """
        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.order_processing_internal_location,
            product_list=[self.salesable_product]
        )

        # Test that no Journal Entry move is generated
        self.assertFalse(stock_picking_order.account_move_ids)
        # Test that no stock valuation layer is generated
        self.assertFalse(stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids)

    def test_04_internal_transit_no_company_no_account(self):
        """
            Input:
                Transit location that has
                    - NO valuation accounts
                    - NO company
            Expect:
                generated 1 stock valuation 
                generated 1 journal entry
        """
        self.assertRecordValues(self.inter_company_transit_location, [{
            'valuation_in_account_id': False,
            'valuation_out_account_id': False,
            'company_id': False,
        }])

        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_company_transit_location,
            product_list=[self.salesable_product]
        )

        # Because transit location has no company, therefore
        # Expect 1 Journal Entry (account_move) is generated
        self.assertEqual(len(stock_picking_order.account_move_ids), 1)
        self.assertEqual(stock_picking_order.account_moves_count, 1)

        # Expect 1 stock valuation layer is generated
        self.assertEqual(len(stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids), 1)

    def test_04_internal_transit_no_account(self):
        """
            Input:
                Transit location that has
                    - company
                    - but NO valuation account
            Expect:
                No stock valuation generated
                No journal entry generated
        """

        self.inter_warehouse_transit_location.write({
            'valuation_in_account_id': False,
            'valuation_out_account_id': False,
        })

        # this transit location has no valuation account
        self.assertFalse(self.inter_warehouse_transit_location.valuation_in_account_id)
        self.assertFalse(self.inter_warehouse_transit_location.valuation_out_account_id)

        # this transit location has no company
        self.assertTrue(self.inter_warehouse_transit_location.company_id)

        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_warehouse_transit_location,
            product_list=[self.salesable_product]
        )

        # Because transit location has company, therefore
        # Expect no Journal Entry (account_move) is generated
        self.assertRecordValues(stock_picking_order, [{
            'account_move_ids': [],
            'account_moves_count': 0,
        }])

        # Expect no stock valuation layer is generated
        self.assertFalse(stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids)

    def test_05_internal_transit_has_company_no_account(self):
        """
            Input:
                Transit location that has
                    - both valuation accounts
                    - NO company
            Expect:
                generated 1 stock valuation 
                generated 1 journal entry
        """
        self.inter_company_transit_location.write({
            'company_id': False,
            'valuation_in_account_id': self.stock_val_acc_in.id,
            'valuation_out_account_id': self.stock_val_acc_out.id,
        })

        self.assertRecordValues(self.inter_company_transit_location, [{
            'valuation_in_account_id': self.stock_val_acc_in.id,
            'valuation_out_account_id': self.stock_val_acc_out.id,
            'company_id': False,
        }])

        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_company_transit_location,
            product_list=[self.salesable_product]
        )

        # Because transit location has no company, therefore
        # Expect 1 Journal Entry (account_move) is generated
        self.assertEqual(len(stock_picking_order.account_move_ids), 1)
        self.assertEqual(stock_picking_order.account_moves_count, 1)

        # Expect 1 stock valuation layer is generated
        self.assertEqual(len(stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids), 1)

    def test_06_internal_transit(self):
        """
            Test transfer from Internal to Transit
            Input
                Transit location has both Valuation Accounts and Company
                Product has Standard cost method and Manual valuation
            Expect:
                Generated 1 account valuation layer
                NO journal entry generated
        """
        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_warehouse_transit_location,
            product_list=[self.furniture_product]
        )

        # Expect the product has these settings
        self.assertRecordValues(self.furniture_product.categ_id, [{
            'property_cost_method': 'standard',
            'property_valuation': 'manual_periodic'
        }])

        # Test that no Journal Entry move is generated
        self.assertFalse(stock_picking_order.account_move_ids)

        # Test that no stock valuation layer (svl) is generated
        svl = stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids
        self.assertTrue(svl)
        self.assertRecordValues(svl, [{
            'product_id': self.furniture_product.id,
            'quantity':-1,
            'value': self.furniture_product.standard_price * -1  # -78.00
        }])

    def test_07_internal_transit(self):
        """
            Test transfer from Internal to Transit
            Input
                Transit location has both Valuation Accounts and Company
                Product has Standard cost method and Automated valuation
            Expect:
                Generated 1 account valuation layer
                    quantity:        -1
                    total value:     -300
                Generated 1 journal entry
                                             |   Debit  |  Credit
                    account IN transit:      |    300   |    0
                    account svl internal:    |     0    |   300
        """
        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_warehouse_transit_location,
            product_list=[self.salesable_product]
        )

        # Expect the product has these settings
        self.assertRecordValues(self.salesable_product.categ_id, [{
            'property_cost_method': 'standard',
            'property_valuation': 'real_time'
        }])

        # Expect the transit location has company assigned
        self.assertTrue(self.inter_warehouse_transit_location.company_id)

        # --------------------->     TEST JOURNAL ENTRY     <------------------------- #

        self.assertEqual(stock_picking_order.account_moves_count, 1)
        self.assertEqual(len(stock_picking_order.account_move_ids), 1)
        self.assertEqual(len(stock_picking_order.account_move_line_ids), 2)
        self.assertEqual(
            stock_picking_order.account_move_ids.stock_picking_id.id,
            stock_picking_order.id,
            "Expect account entry is also linked to this just-created stock picking order."
        )

        acc_svl = self.salesable_product.product_tmpl_id.get_product_accounts().get('stock_valuation', False)

        # aml = account move line
        aml_transit_acc_in = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance > 0)
        aml_acc_svl = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance < 0)

        self.assertEqual(self.salesable_product.standard_price, 300)
        # FROM INTERNAL:
        #    account_id =  Stock Valuation
        #    debit      =    0.0
        #    credit     =  300.0
        #    balance    = -300.0
        # TO TRANSIT:
        #    account_id =  Stock Interim (Received)
        #    debit      =  300.0
        #    credit     =    0.0
        #    balance    =  300.0
        #
        # both the entries are linked to the just created stock picking order
        self.assertRecordValues(aml_acc_svl, [{
            'debit': 0,
            'credit': 300,
            'balance':-300,
            'account_id': acc_svl.id,
            'stock_picking_id': stock_picking_order.id,
        }])
        self.assertRecordValues(aml_transit_acc_in, [{
            'debit': 300,
            'credit': 0,
            'balance': 300,
            'account_id': self.inter_warehouse_transit_location.valuation_in_account_id.id,
            'stock_picking_id': stock_picking_order.id,
        }])

        # --------------------->     TEST STOCK VALUATION     <------------------------- #

        # Expect 1 stock valuation layer (svl) is generated
        svl = stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids
        self.assertEqual(len(svl), 1)

        # Expect: Journal Entry is also linked to the corresponding stock valuation layer.
        self.assertRecordValues(svl, [{
            'id': stock_picking_order.account_move_ids.stock_valuation_layer_ids.id,
            'product_id': self.salesable_product.id,
            'quantity':-1,
            'value':-300.00
        }])

    def test_08_internal_transit(self):
        """
            Test transfer from Internal to Transit
            Input
                Transit location has both Valuation Accounts and Company
                Product has FIFO cost method and Automated valuation
            Expect:
                Generated 1 account valuation layer
                    quantity:        -1
                    total value:     -300
                Generated 1 journal entry
                             |   Debit  |  Credit
                    1 line:  |    300   |    0
                    1 line:  |     0    |   300
        """
        self.salesable_prod_categ.write({
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time'
        })

        self.assertRecordValues(self.salesable_product, [{
            'cost_method': 'fifo',
            'valuation': 'real_time'
        }])
        self.assertTrue(self.inter_warehouse_transit_location.company_id)

        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_warehouse_transit_location,
            product_list=[self.salesable_product]
        )

        # --------------------->     TEST JOURNAL ENTRY     <------------------------- #

        self.assertEqual(stock_picking_order.account_moves_count, 1)
        self.assertEqual(len(stock_picking_order.account_move_ids), 1)
        self.assertEqual(len(stock_picking_order.account_move_line_ids), 2)
        self.assertEqual(
            stock_picking_order.account_move_ids.stock_picking_id.id,
            stock_picking_order.id,
            "Expect account entry is also linked to this just-created stock picking order."
        )

        acc_svl = self.salesable_product.product_tmpl_id.get_product_accounts().get('stock_valuation', False)

        # aml = account move line
        aml_transit_acc_in = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance > 0)
        aml_acc_svl = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance < 0)

        self.assertEqual(self.salesable_product.standard_price, 300)
        # FROM INTERNAL:
        #    account_id =  Stock Valuation
        #    debit      =    0.0
        #    credit     =  300.0
        #    balance    = -300.0
        # TO TRANSIT:
        #    account_id =  Stock Interim (Received)
        #    debit      =  300.0
        #    credit     =    0.0
        #    balance    =  300.0
        #
        # both the entries are linked to the just created stock picking order
        self.assertRecordValues(aml_acc_svl, [{
            'debit': 0,
            'credit': 300,
            'balance':-300,
            'account_id': acc_svl.id,
            'stock_picking_id': stock_picking_order.id,
        }])
        self.assertRecordValues(aml_transit_acc_in, [{
            'debit': 300,
            'credit': 0,
            'balance': 300,
            'account_id': self.inter_warehouse_transit_location.valuation_in_account_id.id,
            'stock_picking_id': stock_picking_order.id,
        }])

        # --------------------->     TEST STOCK VALUATION     <------------------------- #

        # Expect 1 stock valuation layer (svl) is generated
        svl = stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids
        self.assertEqual(len(svl), 1)

        # Expect: Journal Entry is also linked to the corresponding stock valuation layer.
        self.assertRecordValues(svl, [{
            'id': stock_picking_order.account_move_ids.stock_valuation_layer_ids.id,
            'product_id': self.salesable_product.id,
            'quantity':-1,
            'value':-300.00
        }])

    def test_09_transit_internal(self):
        """
            Test transfer from Internal to Transit
            Input
                Transit location has both Valuation Accounts and Company
                Product has Standard cost method and Automated valuation
            Expect:
                Generated 1 account valuation layer
                    quantity:         1
                    total value:     300
                Generated 1 journal entry
                                     |   Debit  |  Credit
                    acc out transit: |    300   |    0
                    acc svl:         |     0    |   300
        """
        self.salesable_prod_categ.write({
            'property_cost_method': 'standard',
            'property_valuation': 'real_time'
        })

        # Transfer 1 product to the transit location first
        self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_warehouse_transit_location,
            product_list=[self.salesable_product]
        )
        # Then transfer the product from the transit to the destination as internal location
        stock_picking_order = self._create_stock_picking_order(
            from_location=self.inter_warehouse_transit_location,
            to_location=self.order_processing_internal_location,
            product_list=[self.salesable_product]
        )

        # Expect the product has these settings
        self.assertRecordValues(self.salesable_product.categ_id, [{
            'property_cost_method': 'standard',
            'property_valuation': 'real_time'
        }])

        # Expect the transit location has company assigned
        self.assertTrue(self.inter_warehouse_transit_location.company_id)

        # --------------------->     TEST JOURNAL ENTRY     <------------------------- #

        self.assertEqual(stock_picking_order.account_moves_count, 1)
        self.assertEqual(len(stock_picking_order.account_move_ids), 1)
        self.assertEqual(len(stock_picking_order.account_move_line_ids), 2)
        self.assertEqual(
            stock_picking_order.account_move_ids.stock_picking_id.id,
            stock_picking_order.id,
            "Expect account entry is also linked to this just-created stock picking order."
        )

        acc_svl = self.salesable_product.product_tmpl_id.get_product_accounts().get('stock_valuation', False)

        # aml = account move line
        aml_account_out = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance < 0)
        aml_acc_svl = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance > 0)

        self.assertEqual(self.salesable_product.standard_price, 300)
        # FROM TRANSIT:
        #    account_id =  Stock Interim (Delivered)
        #    debit      =    0.0
        #    credit     =  300.0
        #    balance    = -300.0
        # TO INTERNAL:
        #    account_id =  Stock Valuation
        #    debit      =  300.0
        #    credit     =    0.0
        #    balance    =  300.0
        #
        # both the entries are linked to the just created stock picking order
        self.assertRecordValues(aml_account_out, [{
            'debit': 0,
            'credit': 300,
            'balance':-300,
            'account_id': self.inter_warehouse_transit_location.valuation_out_account_id.id,
            'stock_picking_id': stock_picking_order.id,
        }])
        self.assertRecordValues(aml_acc_svl, [{
            'debit': 300,
            'credit': 0,
            'balance': 300,
            'account_id': acc_svl.id,
            'stock_picking_id': stock_picking_order.id,
        }])

        # --------------------->     TEST STOCK VALUATION     <------------------------- #

        # Expect 1 stock valuation layer (svl) is generated
        svl = stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids
        self.assertEqual(len(svl), 1, "Expect: this stock picking generates only 1 stock valuation layer.")

        # Expect: Journal Entry is also linked to the corresponding stock valuation layer.
        self.assertRecordValues(svl, [{
            'id': stock_picking_order.account_move_ids.stock_valuation_layer_ids.id,
            'product_id': self.salesable_product.id,
            'quantity': 1,
            'value': self.salesable_product.standard_price  # 300.00
        }])

    def test_11_internal_transit(self):
        """
            Test transfer from Internal to Transit
            Input
                Transit location has both Valuation Accounts and Company
                Product 1 has Standard cost method and Manual    valuation
                Product 2 has FIFO     cost method and AUTOMATED valuation
                Transfer both product 1 and product 2 
            Expect:
                Generated only 1 account valuation layer for the automated product
                    quantity:        -1
                    total value:     -300
                Generated only 1 journal entry for the automated product
                             |  Debit   |  Credit
                    1 line:  |   300    |    0
                    1 line:  |    0     |   300
        """
        self.salesable_prod_categ.write({
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time'
        })

        self.assertRecordValues(self.furniture_product, [{
            'cost_method': 'standard',
            'valuation': 'manual_periodic',
        }])
        self.assertRecordValues(self.salesable_product, [{
            'cost_method': 'fifo',
            'valuation': 'real_time',
        }])

        # Expect the transit location has company assigned
        self.assertTrue(self.inter_warehouse_transit_location.company_id)

        # Transfer from internal- to transit location
        stock_picking_order = self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_warehouse_transit_location,
            product_list=[self.furniture_product, self.salesable_product]
        )

        # --------------------->     TEST JOURNAL ENTRY     <------------------------- #

        # Expect 1 Journal Entry move is generated
        self.assertEqual(stock_picking_order.account_moves_count, 1)
        self.assertEqual(len(stock_picking_order.account_move_ids), 1)
        self.assertEqual(len(stock_picking_order.account_move_line_ids), 2)
        self.assertEqual(
            stock_picking_order.account_move_ids.stock_picking_id.id,
            stock_picking_order.id,
            "Expect account entry is also linked to this just-created stock picking order."
        )

        acc_svl = self.salesable_product.product_tmpl_id.get_product_accounts().get('stock_valuation', False)

        # aml = account move line
        aml_transit_acc_in = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance > 0)
        aml_account_svl = stock_picking_order.account_move_line_ids.filtered(lambda aml: aml.balance < 0)

        self.assertEqual(self.salesable_product.standard_price, 300)
        # FROM INTERNAL:
        #    account_id =  Stock Valuation
        #    debit      =    0.0
        #    credit     =  300.0
        #    balance    = -300.0
        # TO TRANSIT:
        #    account_id =  Stock Interim (Received)
        #    debit      =  300.0
        #    credit     =    0.0
        #    balance    =  300.0
        #
        # both the entries are linked to the just created stock picking order
        #
        # Note:
        #    Only Journal Entry for the product with AUTOMATED valuation
        #    NOT for the product with MANUAL_PERIODIC valuation
        self.assertRecordValues(aml_account_svl, [{
            'debit': 0,
            'credit': 300,
            'balance':-300,
            'account_id': acc_svl.id,
            'stock_picking_id': stock_picking_order.id,
        }])
        self.assertRecordValues(aml_transit_acc_in, [{
            'debit': 300,
            'credit': 0,
            'balance': 300,
            'account_id': self.inter_warehouse_transit_location.valuation_in_account_id.id,
            'stock_picking_id': stock_picking_order.id,
        }])

        # --------------------->     TEST STOCK VALUATION     <------------------------- #

        self.assertEqual(
            len(stock_picking_order.move_line_ids),
            2,
            "Expect: 2 stock move lines are created"
        )

        ml_yes_svl_yes_journal_entry = \
            stock_picking_order.move_line_ids.filtered(lambda ml: ml.move_id.stock_valuation_layer_ids.account_move_id)
        ml_yes_svl_no_journal_entry = \
            stock_picking_order.move_line_ids.filtered(lambda ml: not ml.move_id.stock_valuation_layer_ids.account_move_id)

        self.assertTrue(
            ml_yes_svl_no_journal_entry,
            ("Expect: "
             "There is 1 stock move line that has been recorded in stock valuation layer "
             "but has no Journal Entry generated")
        )
        self.assertTrue(
            ml_yes_svl_yes_journal_entry,
            ("Expect: "
             "There is 1 stock move line that has been recorded in stock valuation layer "
             "and has 1 Journal Entry generated")
        )
        self.assertNotEqual(
            ml_yes_svl_no_journal_entry,
            ml_yes_svl_yes_journal_entry,
            ("Expect: "
             "The move line that has both svl and journal entry and "
             "The move line that has svl but no journal entry "
             "are not identical")
        )

        # Expect 1 stock valuation layer (svl) is generated on each
        self.assertEqual(len(ml_yes_svl_no_journal_entry.move_id.stock_valuation_layer_ids), 1)
        self.assertEqual(len(ml_yes_svl_yes_journal_entry.move_id.stock_valuation_layer_ids), 1)

        self.assertEqual(
            stock_picking_order.account_move_ids.stock_valuation_layer_ids.ids[0],
            ml_yes_svl_yes_journal_entry.move_id.stock_valuation_layer_ids.ids[0],
            "Expect: Journal Entry is also linked to the corresponding stock valuation layer."
        )

        self.assertRecordValues(ml_yes_svl_yes_journal_entry.move_id.stock_valuation_layer_ids, [{
            'product_id': self.salesable_product.id,
            'quantity':-1,
            'value':-300.00,
        }])

    def test_12_internal_transit(self):
        """
            Test transfer from Internal to Transit
            Input
                Transit location has both Valuation Accounts and Company
                Product 1 has FIFO cost method and AUTOMATED valuation
                Product 2 has FIFO cost method and AUTOMATED valuation
                Transfer both product 1 and product 2 
            Expect:
                Generated 1 account valuation layer for each the automated product
                                    quantity     |    total valua
                    furniture prod:    -1        |        -300
                    salesable prod:    -1        |         -78
    
                Generated 1 journal entry for the automated product
                             |  Debit   |  Credit
                    1 line:  |   300    |    0
                    1 line:  |    0     |   300
                Generated 1 journal entry for the automated product
                             |  Debit   |  Credit
                    1 line:  |   78     |    0
                    1 line:  |    0     |    78
        """
        self.salesable_prod_categ.write({
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time'
        })
        self.office_furniture_prod_categ.write({
            'property_cost_method': 'standard',
            'property_valuation': 'real_time'
        })

        self.assertRecordValues(self.furniture_product, [{
            'cost_method': 'standard',
            'valuation': 'real_time',
        }])
        self.assertRecordValues(self.salesable_product, [{
            'cost_method': 'fifo',
            'valuation': 'real_time',
        }])

        # Expect the transit location has company assigned
        self.assertTrue(self.inter_warehouse_transit_location.company_id)

        # Transfer from internal- to transit location
        self._create_stock_picking_order(
            from_location=self.wh_stock_internal_location,
            to_location=self.inter_warehouse_transit_location,
            product_list=[self.furniture_product, self.salesable_product]
        )
        # # Then transfer the product from the transit- to the destination as internal location
        stock_picking_order = self._create_stock_picking_order(
            from_location=self.inter_warehouse_transit_location,
            to_location=self.order_processing_internal_location,
            product_list=[self.furniture_product, self.salesable_product]
        )

        # --------------------->     TEST JOURNAL ENTRY     <------------------------- #

        # Expect 2 Journal Entry move is generated
        self.assertEqual(len(stock_picking_order.account_move_ids), 2)
        self.assertEqual(stock_picking_order.account_moves_count, 2)
        self.assertEqual(len(stock_picking_order.account_move_line_ids), 4)
        self.assertEqual(
            stock_picking_order.account_move_ids.stock_picking_id.id,
            stock_picking_order.id,
            "Expect account entry is also linked to this just-created stock picking order."
        )

        acc_svl = self.salesable_product.product_tmpl_id.get_product_accounts().get('stock_valuation', False)

        aml_furniture_transit_account_out = stock_picking_order.account_move_line_ids.filtered(
            lambda aml: aml.balance < 0 and aml.product_id.id == self.furniture_product.id
        )
        aml_furniture_internal_account_svl = stock_picking_order.account_move_line_ids.filtered(
            lambda aml: aml.balance > 0 and aml.product_id.id == self.furniture_product.id
        )
        aml_salesable_transit_account_out = stock_picking_order.account_move_line_ids.filtered(
            lambda aml: aml.balance < 0 and aml.product_id.id == self.salesable_product.id
        )
        aml_salesable_internal_account_svl = stock_picking_order.account_move_line_ids.filtered(
            lambda aml: aml.balance > 0 and aml.product_id.id == self.salesable_product.id
        )

        self.assertEqual(self.furniture_product.standard_price, 78)
        # FROM TRANSIT:
        #    account_id =  Stock Valuation
        #    debit      =    0.0
        #    credit     =   78.0
        #    balance    =  -78.0
        # TO INTERNAL:
        #    account_id =  Stock Interim (Delivered)
        #    debit      =   78.0
        #    credit     =    0.0
        #    balance    =   78.0
        #
        # both the entries are linked to the just created stock picking order
        self.assertRecordValues(aml_furniture_transit_account_out, [{
            'debit': 0,
            'credit': 78,
            'balance':-78,
            'account_id': self.inter_warehouse_transit_location.valuation_out_account_id.id,
            'stock_picking_id': stock_picking_order.id,
        }])
        self.assertRecordValues(aml_furniture_internal_account_svl, [{
            'debit': 78,
            'credit': 0,
            'balance': 78,
            'account_id': acc_svl.id,
            'stock_picking_id': stock_picking_order.id,
        }])

        self.assertEqual(self.salesable_product.standard_price, 300)
        # FROM TRANSIT:
        #    account_id =  Stock Valuation
        #    debit      =    0.0
        #    credit     =  300.0
        #    balance    = -300.0
        # TO INTERNAL:
        #    account_id =  Stock Interim (Delivered)
        #    debit      =  300.0
        #    credit     =    0.0
        #    balance    =  300.0
        #
        # both the entries are linked to the just created stock picking order
        self.assertRecordValues(aml_salesable_transit_account_out, [{
            'debit': 0,
            'credit': 300,
            'balance':-300,
            'account_id': self.inter_warehouse_transit_location.valuation_out_account_id.id,
            'stock_picking_id': stock_picking_order.id,
        }])
        self.assertRecordValues(aml_salesable_internal_account_svl, [{
            'debit': 300,
            'credit': 0,
            'balance': 300,
            'account_id': acc_svl.id,
            'stock_picking_id': stock_picking_order.id,
        }])

        # --------------------->     TEST STOCK VALUATION     <------------------------- #

        self.assertEqual(
            len(stock_picking_order.move_line_ids),
            2,
            "Expect: 2 stock move lines are created"
        )
        self.assertEqual(
            len(stock_picking_order.move_line_ids.move_id.stock_valuation_layer_ids),
            2,
            "Expect: 2 stock valuation layer lines are created"
        )
