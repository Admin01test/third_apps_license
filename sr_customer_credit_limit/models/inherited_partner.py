# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import fields, models, api,_


class Partner(models.Model):
    _inherit = "res.partner"
    
    credit_limit_custom = fields.Float(_("Límite de crédito"))
    credit_check = fields.Boolean('Verificar crédito')
    is_hold = fields.Boolean('Poner en espera')
    blocking_limit = fields.Float(string="Límite de bloqueo")
