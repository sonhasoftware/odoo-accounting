from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    ngay_khoa = fields.Date(string="Ngày khóa", required=True)

class GetMonth(models.AbstractModel):
    _name = 'get.month'

    def get_month_value(self, key):
        month = ['mot', 'hai', 'ba', 'bon', 'nam', 'sau', 'bay', 'tam', 'chin', 'muoi', 'muoi_mot', 'muoi_hai']
        value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        index_value = month.index(key)
        return value[index_value]

    def get_month_key(self, key):
        month = ['mot', 'hai', 'ba', 'bon', 'nam', 'sau', 'bay', 'tam', 'chin', 'muoi', 'muoi_mot', 'muoi_hai']
        value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        index_key = value.index(key)
        return month[index_key]
