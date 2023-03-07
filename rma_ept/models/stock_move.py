from odoo import fields, models, api

class stock_move(models.Model):
    _inherit = 'stock.move'

    def write(self,vals):
        if 'state' in vals and self:
            if self[0].picking_code=='incoming' and vals.get('state')=='done':
                rma=self.env['crm.claim.ept'].search([('return_picking_id','=',self[0].picking_id.id)])
                rma and rma.state == 'approve' and rma.write({'state':'process'})
        return super(stock_move,self).write(vals)
