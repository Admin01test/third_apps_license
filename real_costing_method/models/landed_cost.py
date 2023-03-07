from odoo import models,fields,api,_

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def button_validate(self):
        res = super(StockLandedCost,self).button_validate()
        self.calc_landed_cost_withou_lot()
        self.landed_cost_out_qty()
        # stop

        return res


    def landed_cost_out_qty(self):
        move_id = self.env['stock.move.line']
        sale_order_line = self.env['sale.order.line']
        for cost in self:
            valuation_layer_ids = []
            out_qty = 0.0
            out_additional_cost = 0.0
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
                # cost_incom_unit = cost_to_add / remaining_qty
                # line.move_id.write({'price_unit': line.move_id.price_unit + cost_incom_unit})
                if line.quantity == remaining_qty:
                    continue
                if line.quantity > remaining_qty and line.product_id.tracking in ['lot' , 'serial']:
                    cost_incom_unit = cost_to_add / remaining_qty
                    line.move_id.write({'price_unit': line.move_id.price_unit + cost_incom_unit})

                    mv_pool = move_id.search([('move_id.picking_type_id.code','=','outgoing')
                                                 ,('product_id', '=', line.move_id.product_id.id)])
                    for in_move in line.move_id.move_line_ids:
                        for mv_out in mv_pool:
                            if mv_out.move_id.incoming_reference:
                                if (line.move_id.reference in mv_out.move_id.incoming_reference and mv_out.lot_id.id == in_move.lot_id.id and mv_out.product_id.id == in_move.product_id.id):
                                    linked_layer = mv_out.move_id.stock_valuation_layer_ids[:1]
                                    #calc out qty
                                    out_qty = line.quantity - remaining_qty
                                    # calc additional cost for out qty
                                    out_additional_cost = line.additional_landed_cost - cost_to_add
                                    # calc additional cost per unit for out qty
                                    landed_per_unit = out_additional_cost / out_qty
                                    price_unit = (landed_per_unit * mv_out.qty_done) / mv_out.move_id.product_qty
                                    if mv_pool:
                                        valuation_layer = self.env['stock.valuation.layer'].create({
                                            'value': -out_additional_cost,
                                            'unit_cost': 0,
                                            'quantity': 0,
                                            'remaining_qty': 0,
                                            'stock_valuation_layer_id': linked_layer.id,
                                            'description': cost.name,
                                            'stock_move_id': mv_out.move_id.id,
                                            'product_id': line.move_id.product_id.id,
                                            'stock_landed_cost_id': cost.id,
                                            'company_id': cost.company_id.id,
                                        })
                                        linked_layer.remaining_value += out_additional_cost
                                        valuation_layer_ids.append(valuation_layer.id)
                                        unit_price = valuation_layer.stock_move_id.price_unit
                                        new_unit_price = -price_unit + unit_price

                                        print('pricceeeeeeeeee = ',unit_price , price_unit)
                                        valuation_layer.stock_move_id.write({'price_unit': new_unit_price})

        return

    def calc_landed_cost_withou_lot(self):
        incom_ids = self.env['stock.move.incoming.ref']
        for cost in self:
            vals = {}
            for line in self.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                if line.product_id.tracking == 'none':
                    incom_ref = incom_ids.search([('layer_id.stock_move_id.picking_type_id.code', '=', 'outgoing'),
                                                  ('layer_id.stock_move_id.product_id', '=', line.product_id.id),
                                                  ('ref', '=', line.move_id.reference)])
                    remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                    out_qty = line.quantity - remaining_qty
                    # print('out_qty:================ ',line.quantity, remaining_qty, out_qty)
                    cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
                    cost_incom_unit = 0.0
                    if cost_to_add and remaining_qty:
                       cost_incom_unit = cost_to_add / remaining_qty
                    line.move_id.write({'price_unit':line.move_id.price_unit + cost_incom_unit})
                    print('cost_incom_unit:  = ',cost_incom_unit , line.move_id.price_unit)

                    out_additional_cost_ref = (line.additional_landed_cost - cost_to_add) / out_qty
                    print(line.additional_landed_cost, cost_to_add)

                    if line.quantity == remaining_qty:
                        continue
                    if line.quantity > remaining_qty and line.product_id.tracking == 'none':
                        linked_layer = incom_ref.move_id.stock_valuation_layer_ids[:1]
                        # calc additional cost for out qty
                        out_additional_cost = line.additional_landed_cost - cost_to_add
                        # calc additional cost per unit for out qty
                        price_unit = out_additional_cost / out_qty
                        out_cost_add = 0.0
                        if incom_ref:
                            for in_re in incom_ref:
                                if in_re.ref == line.move_id.reference:
                                    out_cost_add = -(out_additional_cost / out_qty)*in_re.qty
                                    print('out_cost ', out_cost_add)
                                    vals = {
                                        'value': -out_cost_add,
                                        'unit_cost': 0,
                                        'quantity': 0,
                                        'remaining_qty': 0,
                                        'stock_valuation_layer_id': linked_layer.id,
                                        'description': cost.name,
                                        'stock_move_id': in_re.layer_id.stock_move_id.id,
                                        'product_id': line.product_id.id,
                                        'stock_landed_cost_id': cost.id,
                                        'company_id': cost.company_id.id,
                                    }

                                    in_re.write({'cost_to_add':out_cost_add})
                                    # valuation_layer = self.env['stock.valuation.layer'].create(vals)
                                    # linked_layer.remaining_value += out_additional_cost
                                    print('move.price_unit --01: ',in_re.move_id.price_unit)
                                    move_price_unit = (in_re.cost_to_add / in_re.move_id.quantity_done) + in_re.move_id.price_unit
                                    in_re.move_id.write({'price_unit': move_price_unit})
                                    print('move.price_unit: ', move_price_unit , in_re.move_id.price_unit)
                                    # print('vaaaalsL ',vals)


                            # move.write({'value': move.price_unit * move.quantity_done})

        # stop
        return
