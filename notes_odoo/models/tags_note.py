# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CustomTag(models.Model):

    _name = "custom.note.tag"
    _description = "Note Tags"

    name = fields.Char('Tag Name', required=True,)
    color = fields.Integer('Color Index')
    active = fields.Boolean(
        string="Active",
        default=True,
    )
