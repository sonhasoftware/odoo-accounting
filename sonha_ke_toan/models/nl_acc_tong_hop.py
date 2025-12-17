from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class NLAccTongHop(models.Model):
    _name = 'nl.acc.tong.hop'

    ACC_AP_D = fields.Many2one('nl.acc.ap.d', string="ACC AP D", store=True)
    ACC_NK_D = fields.Many2one('acc.ap.nk.d', string="ACC AP NK D", store=True)
    ACC_TL_D = fields.Many2one('nl.acc.ap.tl.d', string="ACC AP TL D", store=True)
    ACC_AP_H = fields.Many2one('nl.acc.ap.h', string="ID Header", store=True)

    MA_TK0_ID = fields.Many2one('acc.tai.khoan', string="Nợ", store=True, compute='get_ma_tk_id', readonly=False)
    MA_TK0 = fields.Char(related='MA_TK0_ID.MA', string="Nợ", store=True)

    HANG_HOA = fields.Many2one('acc.hang.hoa', string="Hàng hóa", store=True)

    SO_LUONG = fields.Float("SL", store=True)
    DON_GIA = fields.Float("Đơn giá", store=True, readonly=False, compute="_get_don_gia")
    PS_NO1 = fields.Integer("Thành tiền", store=True, compute="_get_ps_no1", readonly=False)
    TIEN_NTE = fields.Float("Ngoại tệ", store=True, compute="_get_tien_nte")
    VAT = fields.Integer("Vat", store=True, compute="_get_vat")

    # field theo header
    NGAY_CT = fields.Date(string="Ngày CT", store=True)
    CHUNG_TU = fields.Char(string="Chứng từ", store=True)
    CTGS = fields.Char(string="CTGS", store=True, size=30)
    SO_HD = fields.Char(string="Số HĐ", store=True, size=10)
    SERI_HD = fields.Char(string="Seri HĐ", store=True, size=10)
    NGAY_HD = fields.Date(string="Ngày HĐ", store=True)
    MAU_SO = fields.Char(string="Mẫu số", store=True, size=10)
    PT_THUE = fields.Many2one('acc.thue', string="% Thuế", store=True)
    ONG_BA = fields.Char(string="Ông bà", store=True, size=60)
    GHI_CHU = fields.Char(string="Ghi chú", store=True, size=200)

    KHACH_HANG = fields.Many2one('acc.khach.hang', string="Khách hàng", store=True)
    KH_THUE = fields.Char(string="KH Thuế", store=True, size=150)
    MS_THUE = fields.Char(string="Mã số Thuế", store=True, size=20)
    DC_THUE = fields.Char(string="Địa chỉ Thuế", store=True, size=200)

    BO_PHAN = fields.Many2one('acc.bo.phan', string="Bộ phận", store=True)

    # Liên kết đến bảng vụ việc (hợp đồng)
    VVIEC = fields.Many2one('acc.vviec', string="Vụ việc", store=True)

    # Liên kết đến bảng kho
    KHO = fields.Many2one('acc.kho', string="Kho", store=True)

    # Khoản mục (nếu là bảng riêng thì có thể Many2one)
    KHOAN_MUC = fields.Many2one('acc.khoan.muc', string="Khoản mục", store=True)

    TIEN_TE = fields.Many2one('acc.tien.te', string="Tiền tệ", store=True)
    TY_GIA = fields.Float(string="Tỷ giá", store=True)

    # Liên kết đến bảng tài khoản
    MA_TK1_ID = fields.Many2one('acc.tai.khoan', string="Có", store=True)
    MA_TK1 = fields.Char(related='MA_TK1_ID.MA', string="Có", store=True)

    # Liên kết đến bảng đơn vị cơ sở (DVCS)
    DVCS = fields.Many2one('res.company', string="ĐV", store=True, default=lambda self: self.env.company, readonly=True)

    # Liên kết đến bảng chi nhánh
    CHI_NHANH = fields.Many2one('acc.chi.nhanh', string="Chi nhánh", store=True)
    MENU_ID = fields.Many2one('ir.ui.menu', string="MENU", store=True)
    KHACH_HANGC = fields.Many2one('acc.khach.hang', string="KH có", store=True)
    KHOC = fields.Many2one('acc.kho', string="Kho nhận", store=True)
    TINH = fields.Many2one('acc.tinh', string="Vùng", store=True)
    NGUON = fields.Many2one('acc.nguon', string="HTV Chuyển", store=True)
    LOAIDL = fields.Many2one('acc.loaidl', string="Loại DL", store=True)

    HEAD_NO = fields.Char(string="Head No", store=True, size=30)
    SO_LUONG2 = fields.Float(string="SL2", store=True)
    SL_TP = fields.Float(string="SL TP", store=True)
    NHOM_VAT = fields.Char(string="Nhóm hàng", store=True, size=100)
    THUE_NK = fields.Integer(string="Thuế NK", store=True)
    SAN_PHAM = fields.Many2one('acc.san.pham', string="Thành phẩm", store=True)
    SO_LO = fields.Char(string="Lô", store=True, size=30)
    DAT = fields.Date(string="Ngày", store=True)
    SO_LENHSX = fields.Char(string="Lệnh SX", store=True, size=30)

    BTFIRST = fields.Integer("BTFIRST", store=True)
    PS_CO1 = fields.Integer("PS_CO1", store=True)
    NVBH = fields.Many2one('acc.nvbh', string="NVKD", store=True)

    TSCD = fields.Many2one('acc.tscd', string="TSCĐ")

    @api.model
    def action_receive_ids(self, ids):
        if not ids:
            raise ValidationError("Bạn chưa chọn bản ghi nào")
        records = self.browse(ids)
        if len(records) > 1:
            raise ValidationError("Bạn chỉ được phép chọn 1 bản ghi duy nhất!")

        for rec in records:
            if rec.ACC_AP_D:
                model = 'nl.acc.ap.h'
                action_id = self.env.ref('sonha_ke_toan.acc_nl_ap_h_action').id
            elif rec.ACC_NK_D:
                model = 'acc.ap.nk.h'
                action_id = self.env.ref('sonha_ke_toan.acc_nl_ap_h_nk_action').id

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = f"{base_url}/web#id={rec.ACC_AP_H.id}&menu_id={rec.MENU_ID.id}&action={action_id}&model={model}&view_type=form"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',
            }



