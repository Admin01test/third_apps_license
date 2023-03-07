# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class AccountPaymentInstallment(models.TransientModel):
	_name = 'account.payment.installment'
	_description = "Installment Amount Payment" 

	account_move_id = fields.Many2one('account.move', string="Name")
	journal_id = fields.Many2one('account.journal', string="Payment (Journal)")
	name = fields.Char(string="Origin", readonly=True)
	total_amount = fields.Float(string="Payment Amount", readonly=True)
	currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
	company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
	partner_id = fields.Many2one('res.partner', string="Partner")
	payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', required=True,
		help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
		"Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
		"Check: Pay bill by check and print it from Odoo.\n"\
		"Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"\
		"SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
	payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type')
	journal_id = fields.Many2one('account.journal', string='Payment (Journal)', required=True, domain=[('type', 'in',['bank','cash'])])
	invoice_date = fields.Date('Payment Date')
	installment_id = fields.Many2one('installment.account.payment.details', 'Installment Details')


	@api.model
	def default_get(self,default_fields):
		res = super(AccountPaymentInstallment, self).default_get(default_fields)
		context = self._context
		payment_data = {
			'name':context.get('name'), 
			'currency_id': context.get('currency_id'),
			'total_amount': context.get('total_amount'),
			'company_id': context.get('company_id'),
			'account_move_id':context.get('order_id'),
			'partner_id': context.get('partner_id'),
			'invoice_date': context.get('invoice_date'),
			'installment_id': context.get('installment_id'),
		}
		res.update(payment_data)
		if 'journal_id' not in res:
			res['journal_id'] = self.env['account.journal'].search([('company_id', '=', self.env.user.company_id.id), ('type', 'in', ('bank', 'cash'))], limit=1).id
		return res

	@api.onchange('payment_type')
	def _onchange_payment_type(self):
		if self.payment_type:
			return {'domain': {'payment_method_id': [('payment_type', '=', self.payment_type)]}}

	@api.onchange('journal_id')
	def _onchange_journal(self):
		if self.journal_id:
			self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
			# Set default payment method (we consider the first to be the default one)
			payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
			self.payment_method_id = payment_methods and payment_methods[0] or False
			# Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
			payment_type = self.payment_type in ('inbound', 'transfer') and 'inbound' or 'inbound'
			return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
		return {}

	@api.onchange('currency_id')
	def _onchange_currency(self):
		# Set by default the first liquidity journal having this currency if exists.
		domain = [('type', 'in', ('bank', 'cash')), 
				  ('currency_id', '=', self.currency_id.id),
				  ('company_id', '=', self.company_id.id),]
		journal = self.env['account.journal'].search(domain, limit=1)
		if journal:
			return {'value': {'journal_id': journal.id}}

	def action_register_payment(self):
		for record in self:
			payment_data = {
				'currency_id':record.currency_id.id,
				'payment_type':'inbound',
				'partner_type':'customer',
				'partner_id':record.partner_id.id,
				'amount':record.total_amount,
				'journal_id':record.journal_id.id,
				'date':record.invoice_date,
				'ref':record.account_move_id.name,
				'payment_method_id':record.payment_method_id.id,
			}
			account_payment_id = self.env['account.payment'].create(payment_data)
			account_payment_id.action_post()
			domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
			lines = record.account_move_id.line_ids
			payment_lines = account_payment_id.line_ids.filtered_domain(domain)
			for account in payment_lines.account_id:
				(payment_lines + lines)\
					.filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
					.reconcile()
			record.installment_id.update({
				'payment_status': 'paid',
			})
			sale_order_id = self.env['sale.order'].search([('name','ilike', record.account_move_id.invoice_origin)], limit=1)
			installment_payment_ids = self.env['installment.payment.details'].search([('installment_id','in', sale_order_id.ids)])
			if installment_payment_ids:
				for installment in installment_payment_ids:
					if record.installment_id.no_of_installment == installment.no_of_installment \
					and record.installment_id.payment_description == installment.payment_description:
						installment.update({
							'payment_status': 'paid',
						})


