# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class InventoryAdjustment(models.Model):
	_inherit = 'stock.inventory'

	force_date = fields.Datetime(string="Force Date")

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	force_date = fields.Datetime(string="Force Date")


class StockMove(models.Model):
	_inherit = 'stock.move'

	def _action_done(self, cancel_backorder=False):
		force_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
		if self.env.user.has_group('stock_force_date_app.group_stock_force_date'):
			for move in self:
				if move.picking_id:
					if move.picking_id.force_date:
						force_date = move.picking_id.force_date
					else:
						force_date = move.picking_id.scheduled_date
				if move.inventory_id:
					if move.inventory_id.force_date:
						force_date = move.inventory_id.force_date
					else:
						force_date = move.inventory_id.date

		res = super(StockMove, self)._action_done()
		if self.env.user.has_group('stock_force_date_app.group_stock_force_date'):
			if force_date:
				for move in res:
					move.write({'date':force_date})
					if move.move_line_ids:
						for move_line in move.move_line_ids:
							move_line.write({'date':force_date})
					if move.account_move_ids:
						for account_move in move.account_move_ids:
							if move.inventory_id:
								account_move.write({'ref':move.inventory_id.name})

		return res


	def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
		self.ensure_one()
		AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

		move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
		if move_lines:
			date = self._context.get('force_period_date', fields.Date.context_today(self))
			if self.env.user.has_group('stock_force_date_app.group_stock_force_date'):
				if self.picking_id.force_date:
					date = self.picking_id.force_date.date()
			new_account_move = AccountMove.sudo().create({
				'journal_id': journal_id,
				'line_ids': move_lines,
				'date': date,
				'ref': description,
				'stock_move_id': self.id,
				'stock_valuation_layer_ids': [(6, None, [svl_id])],
				'move_type': 'entry',
			})
			new_account_move._post()