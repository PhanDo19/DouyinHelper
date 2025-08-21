# 🔑 Hướng dẫn setup YouTube API - Phiên bản đầy đủ

## ✅ **Bây giờ có 3 chế độ authentication:**

### **🚀 1. OAuth Login (KHUYẾN NGHỊ) - Full Access**
**Sử dụng file `credentials.json` có sẵn**

✅ **Tính năng:**
- Upload video lên YouTube
- Quản lý channel của bạn
- Đọc thống kê kênh riêng
- Tương tác với API đầy đủ

🔧 **Cách sử dụng:**
1. Chạy ứng dụng
2. Chọn **"YES"** trong dialog authentication
3. Browser sẽ mở → Đăng nhập Google account
4. Cho phép ứng dụng truy cập YouTube
5. Hoàn tất! App có full access

### **⚠️ 2. API Key - Read Only Access**
✅ **Tính năng:**
- Đọc thống kê channel công khai
- Xem thông tin video
- Không thể upload

🔧 **Cách sử dụng:**
1. Chạy ứng dụng  
2. Chọn **"NO"** trong dialog authentication
3. Nhập YouTube Data API v3 key
4. Hoàn tất! App có read-only access

**Lấy API Key:**
- [Google Cloud Console](https://console.cloud.google.com/)
- Create project → Enable YouTube Data API v3 → Create API Key

### **🎮 3. Demo Mode**
✅ **Tính năng:**
- Test giao diện đầy đủ
- Sample data để demo
- Không cần authentication

🔧 **Cách sử dụng:**
1. Chạy ứng dụng
2. Chọn **"CANCEL"** trong dialog authentication
3. App chạy với demo data

## � **Lợi ích của OAuth (credentials.json):**

### **So với API Key:**
- ✅ **Upload videos** (API key không thể)
- ✅ **Quản lý channel** của bạn
- ✅ **Không giới hạn quota** nghiêm ngặt
- ✅ **Access personal data** (channel riêng)

### **Thông tin credentials.json hiện tại:**
- ✅ **Project**: goalng-demo
- ✅ **Client ID**: Đã được cấu hình
- ✅ **Client Secret**: Bảo mật
- ✅ **Redirect URI**: localhost (phù hợp desktop app)

## �️ **Bảo mật:**
- OAuth token được lưu trong `token.json`
- Tự động refresh khi hết hạn
- Credentials an toàn với Google OAuth 2.0

## 🎯 **Khuyến nghị:**
1. **Để upload video**: Dùng OAuth (YES)
2. **Chỉ xem stats**: Dùng API Key (NO) 
3. **Demo/Test**: Dùng Demo Mode (CANCEL)

**Bây giờ bạn có tool YouTube hoàn chỉnh với full access!** 🎉
