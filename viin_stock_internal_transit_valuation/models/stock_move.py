from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_valued_types(self):
        vals = super(StockMove, self)._get_valued_types()
        vals.append('internal_transit')
        return vals

    def _get_internal_transit_move_lines(self):
        res = self.env['stock.move.line']
        for move_line in self.mapped('move_line_ids'):
            check_condition_internal_transit = (
                move_line.location_id.usage == 'internal' and
                move_line.location_dest_id.usage == 'transit' and
                move_line.location_dest_id.company_id and
                move_line.location_dest_id.valuation_in_account_id
            )
            check_condition_transit_internal = (
                move_line.location_id.usage == 'transit' and
                move_line.location_id.company_id and
                move_line.location_dest_id.usage == 'internal' and
                move_line.location_id.valuation_out_account_id
            )
            if (check_condition_internal_transit) or (check_condition_transit_internal):
                res |= move_line
        return res

    def _is_internal_transit(self):
        self.ensure_one()
        if self._get_internal_transit_move_lines():
            return True
        return False

    def _account_entry_move(self, qty, description, svl_id, cost):
        super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)
        if self._is_internal_transit():
            company_from = self.mapped('move_line_ids.location_id.company_id')
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if self.location_id.usage == 'transit':
                acc_dest = acc_valuation
            elif self.location_dest_id.usage == 'transit':
                acc_src = acc_dest
                acc_dest = acc_valuation
            self.with_company(company=company_from.id)._create_account_move_line(acc_src, acc_dest, journal_id, qty, description, svl_id, cost)

    def _create_internal_transit_svl(self, forced_quantity=None):
        '''
        This docstring is the explanation for one of the cases, that is marked along the line.
        
        Case:
        'Resupply product ABC from: Wh/Stock -> transit location -> Warehouse Stock B)' 
        
        if the product ABC, for instance, has the cost method = FIFO and has been purchased twice:
            first time purchased 2 units with price 10
            second time purchased 4 units with price 5
        And 3 units of product ABC are needed in the resupply process
            
        Once the Resupply is progressed, 2 stock picking are created by Odoo according to the Reordering Rule. Where:
            The picking (transit -> Warehouse Stock B) has to be standby until 
            the picking (Wh/stock -> Transit) is done
        
        1) After the first picking is validated:
            The standard price of product is updated => the unit cost of product on stock valuation layer will 
            also be updated right away after the first 2 units of the product has been transfered.
        
        Due to this reason
            This function makes sure the stock valuation price unit of the second picking must be identical 
            with the price unit on the first one. 
        '''
        svl_vals_list = []
        for move in self:
            move = move.with_company(company=move.company_id.id)
            valued_move_lines = move._get_internal_transit_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            quantity = forced_quantity or valued_quantity

            internal_transit_vals = dict(move._prepare_common_svl_vals(), remaining_qty=0)

            for line in valued_move_lines:
                if line.location_id.usage == 'internal' and line.location_dest_id.usage == 'transit':
                    out_svl_vals = move.product_id._prepare_out_svl_vals(quantity, move.company_id)
                    internal_transit_vals.update(out_svl_vals)
                    # Please read the docstring part for the explaination of this line code
                    move.move_dest_ids.write({'price_unit': out_svl_vals['unit_cost']})

                elif line.location_id.usage == 'transit' and line.location_dest_id.usage == 'internal':
                    unit_cost = abs(move._get_price_unit())
                    if move.product_id.cost_method == 'standard':
                        unit_cost = move.product_id.standard_price
                    internal_transit_vals.update(move.product_id._prepare_in_svl_vals(quantity, unit_cost))

            if forced_quantity:
                internal_transit_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name

            svl_vals_list.append(internal_transit_vals)

        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
