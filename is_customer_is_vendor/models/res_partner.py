from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    customer = fields.Boolean(compute='_compute_customer', inverse='_inverse_customer', store=True, string="Is Customer")
    supplier = fields.Boolean(compute='_compute_supplier', inverse='_inverse_supplier', store=True, string="Is Supplier")

    @api.depends('customer_rank')
    def _compute_customer(self):
        for partner in self:
            partner.customer = True if partner.customer_rank > 0 else False

    def _inverse_customer(self):
        for partner in self:
            partner.customer_rank = 1 if partner.customer else 0

    @api.depends('supplier_rank')
    def _compute_supplier(self):
        for partner in self:
            partner.supplier = True if partner.supplier_rank > 0 else False

    def _inverse_supplier(self):
        for partner in self:
            partner.supplier_rank = 1 if partner.supplier else 0
