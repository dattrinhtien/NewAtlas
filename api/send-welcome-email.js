import nodemailer from "nodemailer";

export default async function handler(req, res) {
  // Chỉ chấp nhận POST
  if (req.method !== "POST") {
    return res.status(405).json({ success: false, error: "Method Not Allowed" });
  }

  const { email, fullName, packageName, expiresAt } = req.body || {};

  if (!email || !email.includes("@")) {
    return res.status(400).json({ success: false, error: "Email người nhận không hợp lệ" });
  }

  const userDisplayName = fullName && fullName.trim() ? fullName.trim() : email.split("@")[0];
  const pkgName = packageName || "Hội Viên VIP";
  
  let expiryText = "Vĩnh viễn (Trọn đời)";
  if (expiresAt) {
    try {
      const d = new Date(expiresAt);
      expiryText = `${d.getDate().toString().padStart(2, "0")}/${(d.getMonth() + 1).toString().padStart(2, "0")}/${d.getFullYear()}`;
    } catch (e) {
      expiryText = String(expiresAt);
    }
  }

  // Cấu hình Gmail SMTP Transporter
  const transporter = nodemailer.createTransport({
    host: "smtp.gmail.com",
    port: 465,
    secure: true,
    auth: {
      user: process.env.GMAIL_USER || "dat.trinhtien@gmail.com",
      pass: (process.env.GMAIL_APP_PASSWORD || "rcwwdklcdodmrcif").replace(/\s+/g, ""),
    },
  });

  const htmlContent = `
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kích hoạt Hội Viên VIP thành công</title>
</head>
<body style="margin: 0; padding: 0; background-color: #050b14; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #050b14; padding: 30px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 600px; background: #0b1320; border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.8);">
          
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); padding: 32px 24px; text-align: center;">
              <div style="font-size: 36px; margin-bottom: 8px;">🏛️ ⚡</div>
              <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                VI AN Y QUÁN Y HỌC 3D
              </h1>
              <p style="margin: 6px 0 0; color: #bae6fd; font-size: 13px; font-weight: 500;">
                Nền tảng Giải phẫu Bóc tách Đa tầng & Kinh Lạc Huyệt Vị YHCT
              </p>
            </td>
          </tr>

          <!-- Main Body -->
          <tr>
            <td style="padding: 32px 28px;">
              <h2 style="margin: 0 0 16px; color: #38bdf8; font-size: 18px; font-weight: 700;">
                Xin chào ${userDisplayName},
              </h2>
              <p style="margin: 0 0 18px; font-size: 14px; line-height: 1.6; color: #cbd5e1;">
                Chúc mừng bạn! Yêu cầu nâng cấp tài khoản của bạn đã được quản trị viên <strong>phê duyệt và kích hoạt thành công</strong>. Bạn hiện đã sở hữu toàn quyền truy cập chuyên sâu vào hệ sinh thái 3D.
              </p>

              <!-- Package Details Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; margin-bottom: 24px;">
                <tr>
                  <td style="padding: 18px 20px;">
                    <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 6px;">
                      Thông tin gói kích hoạt
                    </div>
                    <div style="font-size: 17px; font-weight: 800; color: #34d399; margin-bottom: 4px;">
                      ⚡ ${pkgName}
                    </div>
                    <div style="font-size: 13px; color: #cbd5e1;">
                      Thời hạn bản quyền: <strong style="color: #f1f5f9;">${expiryText}</strong>
                    </div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-top: 2px;">
                      Tài khoản đăng nhập: <strong style="color: #38bdf8;">${email}</strong>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Unlocked Features -->
              <div style="margin-bottom: 24px;">
                <h3 style="margin: 0 0 12px; font-size: 14px; color: #f1f5f9; text-transform: uppercase; letter-spacing: 0.5px;">
                  🌟 Đặc quyền VIP đã mở khóa:
                </h3>
                <ul style="margin: 0; padding-left: 20px; font-size: 13px; line-height: 1.8; color: #94a3b8;">
                  <li><strong style="color: #e2e8f0;">Bóc tách 8 tầng giải phẫu Z-Anatomy:</strong> Da, Cơ Nông, Cơ Sâu, Xương, Mạch Máu, Thần Kinh, Tạng Phủ & Bạch Huyết.</li>
                  <li><strong style="color: #e2e8f0;">Tra cứu 419 huyệt vị WHO:</strong> Góc châm, độ sâu an toàn, cấu trúc giải phẫu dưới huyệt & cảnh báo tai biến.</li>
                  <li><strong style="color: #e2e8f0;">Lâm sàng YHCT:</strong> 50 Phác đồ bệnh học, Huyệt Đặc Hiệu, Tý Ngọ Lưu Chú, Nạp Giáp, Nạp Tử & Linh Quy Bát Pháp.</li>
                  <li><strong style="color: #e2e8f0;">Hỗ trợ 03 thiết bị:</strong> Tự động đồng bộ trên Máy tính, iPad và Điện thoại.</li>
                </ul>
              </div>

              <!-- CTA Button -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 28px 0 20px;">
                <tr>
                  <td align="center">
                    <a href="https://yhoc3d.trinhtiendat.com" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 700; padding: 14px 32px; border-radius: 10px; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);">
                      🚀 Mở Ứng Dụng & Bắt Đầu Học Ngay
                    </a>
                  </td>
                </tr>
              </table>

              <!-- PWA Install Guide Note -->
              <div style="background: rgba(30, 41, 59, 0.5); border-left: 3px solid #38bdf8; padding: 12px 16px; border-radius: 4px; margin-top: 24px;">
                <p style="margin: 0; font-size: 12px; color: #94a3b8; line-height: 1.6;">
                  💡 <strong style="color: #cbd5e1;">Mẹo dùng trên Điện thoại:</strong> Khi mở trang <a href="https://yhoc3d.trinhtiendat.com" style="color: #38bdf8; text-decoration: none;">yhoc3d.trinhtiendat.com</a> trên Safari (iPhone) hoặc Chrome (Android), bạn chọn <em>"Chia sẻ ➔ Thêm vào MH chính"</em> để cài đặt ứng dụng chạy mượt toàn màn hình như một App thực thụ.
                </p>
              </div>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background: #060d17; padding: 22px 24px; text-align: center; border-top: 1px solid rgba(56, 189, 248, 0.15);">
              <p style="margin: 0 0 6px; font-size: 13px; color: #cbd5e1; font-weight: 600;">
                Vi An Y Quán — Trung Tâm Nghiên Cứu & Đào Tạo Y Học Cổ Truyền
              </p>
              <p style="margin: 0; font-size: 12px; color: #64748b;">
                Hotline / Zalo hỗ trợ kỹ thuật & chuyên môn: <strong style="color: #38bdf8;">0936.380.666</strong>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `;

  try {
    const info = await transporter.sendMail({
      from: '"Vi An Y Quán Y Học 3D" <dat.trinhtien@gmail.com>',
      to: email,
      subject: `🎉 Chúc mừng bạn đã được kích hoạt ${pkgName} - Vi An Y Quán Y Học 3D`,
      html: htmlContent,
    });

    return res.status(200).json({
      success: true,
      messageId: info.messageId,
      message: `Đã gửi email chào mừng thành công tới ${email}`,
    });
  } catch (error) {
    console.error("Lỗi gửi email qua Gmail SMTP:", error);
    return res.status(500).json({
      success: false,
      error: error.message || "Không thể gửi email qua Gmail SMTP",
    });
  }
}
