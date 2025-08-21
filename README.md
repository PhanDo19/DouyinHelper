# 🎬 Douyin to YouTube Tool v1.0.0

[![Release](https://img.shields.io/github/v/release/PhanDo19/DouyinHelper)](https://github.com/PhanDo19/DouyinHelper/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)

**All-in-one tool for downloading Douyin videos and managing YouTube uploads with professional interface.**

## ✨ Features

### 🎥 Video Management
- **Douyin Video Downloader**: Download videos with various quality options
- **YouTube Upload**: Upload videos with metadata and optimization
- **File Organization**: Organized video selection and tracking

### 🔐 Authentication & Security
- **OAuth 2.0**: Secure YouTube authentication with Google OAuth
- **Auto-Login**: Automatic token management and refresh
- **Three-Tier Auth**: OAuth/API Key/Demo mode support
- **Security-First**: Credential protection and token encryption

### 📊 YouTube Integration
- **Real-time Analytics**: Channel statistics and performance insights
- **Upload Management**: Professional upload configuration
- **Channel Dashboard**: Comprehensive channel management
- **Video Optimization**: Automatic optimization for YouTube

### 🎨 Professional UI
- **Modern Interface**: Colorful, intuitive design
- **Responsive Layout**: Scrollable content with proper styling
- **Color Themes**: Professional color schemes
- **User Experience**: Easy-to-use with comprehensive feedback

## 🚀 Quick Start

### 1. Installation
```bash
# Clone repository
git clone https://github.com/PhanDo19/DouyinHelper.git
cd DouyinHelper

# Install dependencies
pip install -r requirements.txt
```

### 2. YouTube API Setup
See [YOUTUBE_API_SETUP.md](YOUTUBE_API_SETUP.md) for detailed instructions.

**Quick Setup:**
- **OAuth (Recommended)**: Full access with credentials.json
- **API Key**: Read-only access for public data
- **Demo Mode**: Test interface without authentication

### 3. Run Application
```bash
python douyin_youtube_tool.py
```
Or use the Windows batch file:
```bash
run_tool.bat
```

## 📋 Requirements

- **Python**: 3.7 or higher
- **Dependencies**: See [requirements.txt](requirements.txt)
- **YouTube API**: Optional (for YouTube features)
- **Google Credentials**: For OAuth authentication

## 🔧 Configuration

### YouTube Authentication Modes

| Mode | Access Level | Features | Setup Required |
|------|-------------|----------|----------------|
| **OAuth** | Full Access | Upload, Manage, Analytics | credentials.json |
| **API Key** | Read Only | Public stats, Channel info | YouTube API Key |
| **Demo** | Interface Only | UI testing, Sample data | None |

### Upload Configuration
- Persistent settings storage
- Metadata customization
- Quality optimization
- Batch upload support

## 📖 Documentation

- **[Setup Guide](YOUTUBE_API_SETUP.md)**: YouTube API configuration
- **[Changelog](CHANGELOG.md)**: Version history and updates
- **[Requirements](requirements.txt)**: Python dependencies

## 🛡️ Security & Privacy

- OAuth 2.0 secure authentication
- Local credential storage
- No data collection
- Push protection compliance
- Sensitive file exclusion (.gitignore)

## 🎯 Use Cases

- **Content Creators**: Download and repost content
- **Channel Managers**: Bulk upload and analytics
- **Developers**: API integration examples
- **Researchers**: Video data collection

## 🔄 Version History

### v1.0.0 (2025-08-21)
- Initial stable release
- YouTube OAuth integration
- Professional UI implementation
- Comprehensive feature set

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**PhanDo19**
- GitHub: [@PhanDo19](https://github.com/PhanDo19)
- Repository: [DouyinHelper](https://github.com/PhanDo19/DouyinHelper)

## ⭐ Support

If you find this tool helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs via Issues
- 💡 Suggesting features
- 🔄 Contributing code

---

**Built with ❤️ using Python & Tkinter**
