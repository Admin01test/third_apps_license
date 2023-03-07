# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.depends('order_line.price_total')
	def _amount_all(self):
		"""
		Compute the total amounts of the SO.
		"""
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
				amount_tax += line.price_tax
			order.update({
				'amount_untaxed': amount_untaxed,
				'amount_tax': amount_tax,
				'amount_total': amount_untaxed + amount_tax,
				'total_payment_amount': amount_untaxed + amount_tax,
			})

	@api.depends('total_payment_amount','down_payment_amount')
	def _compute_payable_amount(self):
		"""
		Compute the total amounts of the SO.
		"""
		for order in self:
			order.update({
				'payable_amount': order.total_payment_amount - order.down_payment_amount,
			})


	@api.depends('installment_month','payable_amount')
	def _compute_installment_amount(self):
		"""
		Compute the total amounts of the SO.
		"""
		for order in self:
			if order.installment_month > 0.0 and order.payable_amount > 0.0:
				order.update({
					'installment_amount': (order.payable_amount / order.installment_month)
				})


	total_payment_amount = fields.Monetary(string='Payment Amount', store=True, readonly=True, compute='_amount_all', copy=False)
	payable_amount = fields.Monetary(string='Installment Payable Amount', store=True, readonly=True, compute='_compute_payable_amount', copy=False)
	down_payment_amount = fields.Float('Down Payment Amount', copy=False)
	installment_month = fields.Integer('Duration(Months)', copy=False)
	next_payment_date = fields.Date('Next Payment Date', copy=False)
	installment_amount = fields.Float('Installment Amount', store=True, readonly=True, compute='_compute_installment_amount', copy=False)
	installment_details_ids = fields.One2many('installment.payment.details','installment_id','Account Payment Installment', copy=False)
	payment_installment_group = fields.Boolean(compute="compute_payment_installment_group", string='Account Payment Installment')


	@api.model
	def default_get(self, fields):
		res = super(SaleOrder, self).default_get(fields)
		if res:
			if self.env.user.has_group('account_payment_installment_app.group_account_payment_installment'):
				res.update({'payment_installment_group': True})
			else:
				res.update({'payment_installment_group': False})
		return res

	@api.model
	def compute_payment_installment_group(self):
		if self.env.user.has_group('account_payment_installment_app.group_account_payment_installment'):
			self.payment_installment_group = True
		else:
			self.payment_installment_group = False

	def action_confirm(self):
		result = super(SaleOrder, self).action_confirm()
		for num in range(0,self.installment_month + 1):
			if num == 0:
				new_record = self.env['installment.payment.details'].create({
					'no_of_installment': num,
					'payment_date':  self.date_order,
					'payment_amount': self.down_payment_amount,
					'payment_description': 'Down Payment Amount',
					'payment_status': 'draft',
					'installment_id': self.id
				})
			else:
				next_payment_date = fields.Datetime.from_string(self.next_payment_date)
				if num == 1:
					new_record = self.env['installment.payment.details'].create({
						'no_of_installment': num,
						'payment_date': next_payment_date,
						'payment_amount': self.installment_amount,
						'payment_description': str(num) + ' Installment Amount',
						'payment_status': 'draft',
						'installment_id': self.id
					})
				else:
					next_payment_date = next_payment_date + relativedelta(months=(num - 1)  or 0.0)
					new_record = self.env['installment.payment.details'].create({
						'no_of_installment': num,
						'payment_date': next_payment_date,
						'payment_amount': self.installment_amount,
						'payment_description': str(num) + ' Installment Amount',
						'payment_status': 'draft',
						'installment_id': self.id
					})
		return result


	def _prepare_invoice(self):
		result = super(SaleOrder, self)._prepare_invoice()
		if result:
			result.update({
				'down_payment_amount': self.down_payment_amount,
				'installment_month': self.installment_month,
				'next_payment_date': self.next_payment_date,
			})
		return result


	def action_cancel(self):
		result = super(SaleOrder, self).action_cancel()
		if result:
			installment_details_ids = self.mapped('installment_details_ids')
			if installment_details_ids:
				installment_details_ids.unlink()
		return result


class InstallmentPaymentDetails(models.Model):
	_name = 'installment.payment.details'
	_description = "Installment Payment Details"

	installment_id = fields.Many2one('sale.order', 'Installment Details')
	no_of_installment = fields.Integer('#No')
	payment_date = fields.Date('Payment Date')
	payment_amount = fields.Float('Payment Amount')
	payment_description = fields.Text('Payment Description')
	payment_status = fields.Selection([
		('draft', 'Draft'),
		('paid', 'Paid'),
		], string='Payment Status', readonly=True, default='draft')
