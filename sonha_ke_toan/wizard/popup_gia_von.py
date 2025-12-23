from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class PopupGiaVon(models.TransientModel):
    _name = "popup.gia.von"
    _inherit = ['get.month']

    thang = fields.Selection([('mot', 1),
                              ('hai', 2),
                              ('ba', 3),
                              ('bon', 4),
                              ('nam', 5),
                              ('sau', 6),
                              ('bay', 7),
                              ('tam', 8),
                              ('chin', 9),
                              ('muoi', 10),
                              ('muoi_mot', 11),
                              ('muoi_hai', 12), ], string="Tháng", store=True,
                             default=lambda self: self._get_default_month())
    nam = fields.Integer(string="Năm", store=True, default=lambda self: self.default_nam())

    @api.constrains('nam')
    def _check_nam(self):
        for r in self:
            if r.nam <= 0:
                raise ValidationError("Năm không thể nhỏ hơn 1!")

    def get_month(self):
        return self.get_month_value(self.thang)

    def _get_default_month(self):
        now = datetime.now().date()
        month = now.month
        return self.get_month_key(month)

    def default_nam(self):
        now = datetime.now().date()
        return now.year

    def action_handle(self):
        company = self.env.company.id
        if self.thang:
            thang = self.get_month()
        else:
            thang = datetime.now().date().month
        from_date = date(self.nam, thang, 1)
        to_date = from_date + relativedelta(months=1) - timedelta(days=1)
        query = "SELECT * FROM fn_tinh_gia_von_tb_thang(%s, %s, date %s)"
        self.env.cr.execute(query, (company, from_date, to_date))
        result = self.env.cr.dictfetchone()
        raise ValidationError(result["fn_tinh_gia_von_tb_thang"])
