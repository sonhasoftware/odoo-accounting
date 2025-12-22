from odoo import models, fields, api
from datetime import datetime


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
        pass

    def action_view(self):
        pass