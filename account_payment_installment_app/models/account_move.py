# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
	_inherit = "account.move"


	@api.depends(
		'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.debit',
		'line_ids.credit',
		'line_ids.currency_id',
		'line_ids.amount_currency',
		'line_ids.amount_residual',
		'line_ids.amount_residual_currency',
		'line_ids.payment_id.state',
		'line_ids.full_reconcile_id')
	def _amount_all(self):
		"""
		Compute the total amounts of the SO.
		"""
		for move in self:
			move.update({
				'total_payment_amount': move.amount_untaxed + move.amount_tax,
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
	installment_details_ids = fields.One2many('installment.account.payment.details','installment_id','Account Payment Installment', copy=False)
	payment_installment_group = fields.Boolean(compute="compute_payment_installment_group", string='Account Payment Installment')


	@api.model
	def default_get(self, fields):
		res = super(AccountMove, self).default_get(fields)
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


	def action_post(self):
		result = super(AccountMove, self).action_post()
		total_installment_amount = 0.0
		for num in range(0,self.installment_month + 1):
			total_installment_amount += self.down_payment_amount
			if num == 0:
				new_record = self.env['installment.account.payment.details'].create({
					'no_of_installment': num,
					'payment_date':  self.invoice_date,
					'payment_amount': self.down_payment_amount,
					'payment_description': 'Down Payment Amount',
					'payment_status': 'draft',
					'installment_id': self.id
				})
			else:
				next_payment_date = fields.Datetime.from_string(self.next_payment_date)
				if num == 1:
					total_installment_amount += self.installment_amount
					new_record = self.env['installment.account.payment.details'].create({
						'no_of_installment': num,
						'payment_date': next_payment_date,
						'payment_amount': self.installment_amount,
						'payment_description': str(num) + ' Installment Amount',
						'payment_status': 'draft',
						'installment_id': self.id
					})
				else:
					total_installment_amount += self.installment_amount
					next_payment_date = next_payment_date + relativedelta(months=(num - 1)  or 0.0)
					new_record = self.env['installment.account.payment.details'].create({
						'no_of_installment': num,
						'payment_date': next_payment_date,
						'payment_amount': self.installment_amount,
						'payment_description': str(num) + ' Installment Amount',
						'payment_status': 'draft',
						'installment_id': self.id
					})
		return result


	def button_cancel(self):
		result = super(AccountMove, self).button_cancel()
		if result:
			installment_details_ids = self.mapped('installment_details_ids')
			if installment_details_ids:
				installment_details_ids.unlink()
		return result


class InstallmentAccountPaymentDetails(models.Model):
	_name = 'installment.account.payment.details'
	_description = "Installment Payment Details"

	installment_id = fields.Many2one('account.move', 'Installment Details')
	installment_sale_id = fields.Many2one('installment.payment.details', 'Installment Sale Details')
	partner_id = fields.Many2one('res.partner', string="Partner", related='installment_id.partner_id')
	state = fields.Selection(related='installment_id.state', string="Status", store=True, readonly=True)
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
	no_of_installment = fields.Integer('#No')
	payment_date = fields.Date('Payment Date')
	payment_amount = fields.Float('Payment Amount', digits='Product Price')
	amount_residual = fields.Monetary(related='installment_id.amount_residual', string="Amount Due", store=True, readonly=True)
	payment_description = fields.Text('Payment Description')
	payment_status = fields.Selection([
		('draft', 'Draft'),
		('paid', 'Paid'),
		], string='Payment Status', readonly=True, default='draft')


	def action_invoice_payment(self):
		view_id = self.env.ref('account_payment_installment_app.account_payment_installment_wizard')
		if view_id:
			pay_wiz_data={
				'name' : _('Installment Payment'),
				'type' : 'ir.actions.act_window',
				'view_type' : 'form',
				'view_mode' : 'form',
				'res_model' : 'account.payment.installment',
				'view_id' : view_id.id,
				'target' : 'new',
				'context' : {
							'name': self.installment_id.name,
							'order_id':self.installment_id.id,
							'total_amount':self.payment_amount,
							'company_id':self.company_id.id,
							'currency_id':self.currency_id.id,
							'invoice_date':self.payment_date,
							'partner_id':self.partner_id.id,
							'installment_id': self.id
							 },
			}
		return pay_wiz_data


	def _installment_reminder_email(self):
		installment_ids = self.search([('payment_status','=','draft'),
									   ('state','=','posted'),
									   ('installment_id.amount_residual','!=',0.0)])
		for record in installment_ids:
			if not isinstance(record.payment_date, bool):
				today = datetime.now().date()
				date_two_days_before = record.payment_date - timedelta(days=2)
				if date_two_days_before == today:
					template_id = self.env.ref('account_payment_installment_app.email_template_installment_payment_date_remainder')
					if template_id:
						values = template_id.sudo().generate_email(record.id,['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
						values['email_to'] = record.partner_id.email or ''
						values['author_id'] = self.env.user.partner_id.id
						values['subject'] = "Remainder about installment payment date on "+ str(record.payment_date)
						mail_mail_obj = self.env['mail.mail']
						msg_id = mail_mail_obj.sudo().create(values)
						if msg_id:
							msg_id.sudo().send()
				else:
					pass						
		return True