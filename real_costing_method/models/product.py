# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Rightechs (<http://www.Rightechs.net/>)
#               <contact@rightechs.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from odoo import models, fields, api, _
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from datetime import datetime
from odoo.tools import float_is_zero
import time


class Product(models.Model):
    _inherit = 'product.product'

    def _prepare_out_svl_vals(self, quantity, company, move=False):
        """Prepare the values for a stock valuation layer created by a delivery.

        :param quantity: the quantity to value, expressed in `self.uom_id`
        :return: values to use in a call to create
        :rtype: dict
        """
        self.ensure_one()
        if not move:
            return super(Product, self)._prepare_out_svl_vals(quantity, company)
        # Quantity is negative for out valuation layers.
        quantity = -1 * quantity
        vals = {
            'product_id': self.id,
            'value': quantity * self.standard_price,
            'unit_cost': self.standard_price,
            'quantity': quantity,
        }
        if self.cost_method in ('average', 'fifo'):
            fifo_vals = self._run_fifo(abs(quantity), company, move)
            vals['remaining_qty'] = fifo_vals.get('remaining_qty')
            if self.cost_method == 'fifo':
                vals.update(fifo_vals)
        return vals

    def _run_fifo(self, quantity, company, move=False):
        self.ensure_one()
        if not move:
            return super(Product, self)._run_fifo(quantity, company)
        # Find back incoming stock valuation layers (called candidates here) to value `quantity`.
        qty_to_take_on_candidates = quantity
        candidate_used = []
        domain = [
            ('product_id', '=', self.id),
            ('remaining_qty', '>', 0),
            ('company_id', '=', company.id),
        ]
        candidates = self.env['stock.valuation.layer'].sudo(
        ).with_context(active_test=False).search(domain)

        new_standard_price = 0
        qty_taken_on_candidate = 0.0
        incom_ids = []
        tmp_value = 0  # to accumulate the value taken on the candidates
        candidate_filtered = []
        if move.product_id.tracking in ['lot', 'serial'] and move.product_id.cost_method == 'fifo':
            for out_move_line in move.move_line_ids:
                if not out_move_line.lot_id:
                    continue
                for layer in candidates:
                    m_l_ids = self.env['stock.move.line'].search([('move_id', '=', layer.stock_move_id.id),
                                                                  ('lot_id', '=',
                                                                   out_move_line.lot_id.id),
                                                                  ('product_id', '=', out_move_line.product_id.id)])

                    if m_l_ids:
                        for ml in m_l_ids:
                            candidate_filtered.append(layer)
            candidates = candidate_filtered

        if self.tracking in ['lot', 'serial']:
            for candidate in candidates:

                for incom_move in candidate.stock_move_id.move_line_ids:
                    for out_move in move.move_line_ids:

                        if out_move.lot_id.id == incom_move.lot_id.id:

                            if candidate.remaining_qty <= out_move.qty_done:
                                qty_taken_on_candidate = candidate.remaining_qty
                            else:
                                qty_taken_on_candidate = out_move.qty_done
                            candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty

                            new_standard_price = candidate_unit_cost

                            value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
                            value_taken_on_candidate = candidate.currency_id.round(
                                value_taken_on_candidate)
                            new_remaining_value = candidate.remaining_value - value_taken_on_candidate

                            qty_to_take_on_candidates -= qty_taken_on_candidate
                            tmp_value += value_taken_on_candidate

                            candidate.write(
                                {'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate})
                            candidate.write(
                                {'remaining_value': candidate.remaining_qty * candidate.unit_cost})
                            candidate_used.append(
                                candidate.stock_move_id.reference)

                            if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
                                break

        else:
            for candidate in candidates:

                qty_taken_on_candidate = min(
                    qty_to_take_on_candidates, candidate.remaining_qty)

                candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty

                new_standard_price = candidate_unit_cost
                value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
                value_taken_on_candidate = candidate.currency_id.round(
                    value_taken_on_candidate)
                new_remaining_value = candidate.remaining_value - value_taken_on_candidate

                qty_to_take_on_candidates -= qty_taken_on_candidate
                tmp_value += value_taken_on_candidate
                candidate.write(
                    {'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate})
                candidate.write(
                    {'remaining_value': candidate.remaining_qty * candidate.unit_cost})

                in_vals = {
                    'ref': candidate.stock_move_id.reference,
                    'qty': qty_taken_on_candidate,
                    # 'move_id' : move,
                }
                incom_ids.append((0, 0, in_vals))

                if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
                    break

        if new_standard_price and self.cost_method == 'fifo':
            self.sudo().with_context(force_company=company.id).standard_price = new_standard_price

        # If there's still quantity to value but we're out of candidates, we fall in the
        # negative stock use case. We chose to value the out move at the price of the
        # last out and a correction entry will be made once `_fifo_vacuum` is called.
        vals = {}
        if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
            vals = {
                'value': -tmp_value,
                'unit_cost': tmp_value / quantity,
            }

        else:
            assert qty_to_take_on_candidates > 0
            last_fifo_price = new_standard_price or self.standard_price
            negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
            tmp_value += abs(negative_stock_value)
            vals = {
                'remaining_qty': -qty_to_take_on_candidates,
                'value': -tmp_value,
                'unit_cost': last_fifo_price,
            }

        if self.tracking == 'none':
            # RIGHTECHS CUSTOMIZATION
            vals.update({"incom_ref_line": incom_ids})

        # stop

        return vals


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    incoming_reference = fields.Char('Incoming Ref.', readonly=1)
    incom_ref_line = fields.One2many(
        'stock.move.incoming.ref', 'layer_id', 'Incoming Ref.')


class StockMove(models.Model):
    _inherit = "stock.move"

    incoming_reference = fields.Char('Incoming Ref.', readonly=1)
    incom_ref_line = fields.One2many(
        'stock.move.incoming.ref', 'move_id', 'Incoming Ref.')

    def _create_in_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_in_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
                                                                                     move.product_id.uom_id)
            # May be negative (i.e. decrease an out move).
            unit_cost = abs(move._get_price_unit())
            if move.product_id.cost_method == 'standard':
                unit_cost = move.product_id.standard_price
            svl_vals = move.product_id._prepare_in_svl_vals(
                forced_quantity or valued_quantity, unit_cost)
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals[
                    'description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
            svl_vals_list.append(svl_vals)
        layer = self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
        if layer.stock_move_id.origin_returned_move_id:
            layer.write({'unit_cost': -layer.stock_move_id.origin_returned_move_id.price_unit,
                         'value': -layer.stock_move_id.origin_returned_move_id.price_unit * layer.quantity})
        return layer

    def _create_out_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_out_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
                                                                                     move.product_id.uom_id)

            if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                continue
            svl_vals = move.product_id._prepare_out_svl_vals(
                forced_quantity or valued_quantity, move.company_id, move)
            svl_vals.update(move._prepare_common_svl_vals())

            if forced_quantity:
                svl_vals[
                    'description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
            svl_vals_list.append(svl_vals)
        layer = self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

        for lay in layer:
            layer.incom_ref_line.write({'move_id': lay.stock_move_id.id})

            lay.write({'remaining_value': 0.0})
            lay.write({'unit_cost': lay.unit_cost * -1})
            lay.stock_move_id.write({'price_unit': lay.unit_cost})
        # layer.write({'value':layer.unit_cost * layer.quantity})
        # stop
        return layer

    def _action_done(self, cancel_backorder=False):
        # res =
        qty = 0.0
        value = 0.0
        purchase_price = 0.0
        incoming_ref = []
        for move in self:
            if move.stock_valuation_layer_ids:
                for mvl in move.stock_valuation_layer_ids:
                    qty += mvl.quantity
                    value += mvl.value
                    purchase_price = value / qty

                    move.write({'price_unit': purchase_price})

            if move.product_id.tracking in ['lot', 'serial'] and move.picking_type_id.code == 'outgoing':
                for line in move.move_line_ids:
                    m_l_ids = self.env['stock.move.line'].search([('move_id.state', '=', 'done'),
                                                                  ('move_id.picking_type_id.code',
                                                                   '=', 'incoming'),
                                                                  ('lot_id', '=',
                                                                   line.lot_id.id),
                                                                  ('product_id', '=', move.product_id.id)])
                    if m_l_ids:
                        for ml in m_l_ids:
                            incoming_ref.append(ml.move_id.reference)
                        # ADD Reference off reciept order to delivered order to compute landed cost for qty already out
                        move.write(
                            {'incoming_reference': ' ,'.join(incoming_ref), })

        return super(StockMove, self)._action_done(cancel_backorder)


class IncomingMoveReference(models.Model):
    _name = 'stock.move.incoming.ref'

    ref = fields.Char('Incoming Ref')
    qty = fields.Float('QTY')
    cost_to_add = fields.Float('Cost To Add')
    move_id = fields.Many2one('stock.move')
    layer_id = fields.Many2one('stock.valuation.layer')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for l in self.move_ids_without_package:
            if l.origin_returned_move_id and l.product_id.categ_id.property_cost_method == 'fifo':
                l.write({'price_unit': -l.origin_returned_move_id.price_unit})
        return res
