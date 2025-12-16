from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccNguon(models.Model):
    _name = 'acc.nguon'
    _order = 'MA,CAP,DVCS'
    _rec_name = 'MA_TEN'

    CAP = fields.Integer(string="Cấp", store=True)
    MA = fields.Char(string="Mã", store=True)
    TEN = fields.Char(string="Tên", store=True)
    MA_TEN = fields.Char(string="Mã - Tên", store=True, readonly=True, compute="get_ma_ten")
    NGUON = fields.Integer(string="Nguồn", store=True, readonly=True)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)
    ACTIVE = fields.Boolean(string="ACTIVE", store=True)

    @api.depends('MA', 'TEN')
    def get_ma_ten(self):
        for r in self:
            r.MA_TEN = f"{r.MA} - {r.TEN}" if (r.MA and r.TEN) else ""

    def create(self, vals):
        rec = super(AccNguon, self).create(vals)
        rec.NGUON = rec.id
        dvcs = rec.DVCS.id
        self.env.cr.execute("CALL public.update_cap(%s, %s);", ['acc_nguon', dvcs])
        return rec

    @api.constrains('MA')
    def _check_unique_ma(self):
        for rec in self:
            if rec.MA:
                exists = self.search([
                    ('MA', '=', rec.MA),
                    ('id', '!=', rec.id)
                ], limit=1)
                if exists:
                    raise ValidationError("Mã %s đã tồn tại, vui lòng nhập mã khác!" % rec.MA)