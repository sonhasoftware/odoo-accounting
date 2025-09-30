from odoo import api, fields, models


class SonhaUser(models.Model):
    _name = 'sonha.user'

    name = fields.Char(string="Tên User", store=True)
    user_id = fields.Many2one("res.users", string="Người dùng", store=True)

    def action_phan_quyen(self):
        for r in self:
            list_model = self.env['ir.model'].sudo().search([('model', '=', 'acc.tai.khoan')])
            for model in list_model:
                list_company = r.user_id.company_ids
                for company in list_company:
                    check = self.env['sonha.phan.quyen'].sudo().search([('TEN_BANG', '=', model.id),
                                                                        ('NGUOI_DUNG', '=', r.id),
                                                                        ('DVCS', '=', company.id),])

                    if not check:
                        self.env['sonha.phan.quyen'].sudo().create({
                            'NGUOI_DUNG': r.id,
                            'TEN_BANG': model.id,
                            'DVCS': company.id,
                        })


class ResUsers(models.Model):

    _inherit = "res.users"

    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        self.env['sonha.user'].sudo().create({
            "name": user.name,
            "user_id": user.id
        })

        return user
