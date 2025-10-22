# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CustomStage(models.Model):

    _name = "custom.note.stage"
    _description = "Notes Categories"

    name = fields.Char('Name', translate=True, required=True)
    fold = fields.Boolean('Folded by Default')
    active = fields.Boolean(
        string="Active",
        default=True,
    )