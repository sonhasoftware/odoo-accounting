from odoo import api, fields, models


class SonhaUser(models.Model):
    _name = 'sonha.user'
    _rec_name = 'NAME'

    SONHA_USER = fields.Integer(string="User id", store=True)
    NAME = fields.Char(string="Tên", store=True)
    NGUOI_DUNG = fields.Many2one("res.users", string="Người dùng", store=True)
    NGAY_KHOA = fields.Date(string="Ngày khóa", store=True)
    SO_NGAY_KHOA = fields.Integer(string="Số ngày khóa", store=True)
    USER_KHAI_THAC = fields.Boolean(string="User khai thác", store=True)

    def action_phan_quyen(self):
        for r in self:
            list_model = self.env['ir.model'].sudo().search([])
            list_model = list_model.filtered(lambda x: x.modules == 'sonha_ke_toan')
            for model in list_model:
                list_company = self.env.company
                for company in list_company:
                    check = self.env['sonha.phan.quyen'].sudo().search([('TEN_BANG', '=', model.id),
                                                                        ('NGUOI_DUNG_ID', '=', r.id),
                                                                        ('DVCS', '=', company.id),])

                    if not check:
                        self.env['sonha.phan.quyen'].sudo().create({
                            'NGUOI_DUNG_ID': r.id,
                            'TEN_BANG': model.id,
                            'DVCS': company.id,
                            'NGUOI_DUNG': r.NGUOI_DUNG.id or 0,
                            'SONHA_USER': r.id or 0,
                        })

    def create(self, vals):
        rec = super(SonhaUser, self).create(vals)
        rec.SONHA_USER = rec.id
        return rec


class ResUsers(models.Model):

    _inherit = "res.users"

    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        self.env['sonha.user'].sudo().create({
            "NAME": user.name,
            "NGUOI_DUNG": user.id
        })

        return user
