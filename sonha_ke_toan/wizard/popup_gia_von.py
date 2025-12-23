from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class PopupGiaVon(models.TransientModel):
    _name = "popup.gia.von"

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
        if self.thang == 'mot':
            return 1
        elif self.thang == 'hai':
            return 2
        elif self.thang == 'ba':
            return 3
        elif self.thang == 'bon':
            return 4
        elif self.thang == 'nam':
            return 5
        elif self.thang == 'sau':
            return 6
        elif self.thang == 'bay':
            return 7
        elif self.thang == 'tam':
            return 8
        elif self.thang == 'chin':
            return 9
        elif self.thang == 'muoi':
            return 10
        elif self.thang == 'muoi_mot':
            return 11
        elif self.thang == 'muoi_hai':
            return 12
        else:
            return None

    def _get_default_month(self):
        now = datetime.now().date()
        month = now.month
        if month == 1:
            return 'mot'
        elif month == 2:
            return 'hai'
        elif month == 3:
            return 'ba'
        elif month == 4:
            return 'bon'
        elif month == 5:
            return 'nam'
        elif month == 6:
            return 'sau'
        elif month == 7:
            return 'bay'
        elif month == 8:
            return 'tam'
        elif month == 9:
            return 'chin'
        elif month == 10:
            return 'muoi'
        elif month == 11:
            return 'muoi_mot'
        elif month == 12:
            return 'muoi_hai'
        else:
            return None

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
        query = "SELECT * FROM fn_tinh_gia_von_tb_thang(%s, %s, %s)"
        self.env.cr.execute(query, (company, from_date, to_date))
        result = self.env.cr.dictfetchone()
        raise ValidationError(result["fn_tinh_gia_von_tb_thang"])

    def action_view(self):
        pass