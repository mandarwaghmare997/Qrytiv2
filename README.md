# Qrytiv2 - ISO 42001 AI Governance Platform

A comprehensive platform for AI governance and compliance management, built with React frontend and Flask backend.

## 🚀 Live Application

**Production URL:** https://app.qryti.com

## 🏗️ Architecture

### Frontend
- **Framework:** React 19.1.0 with Vite
- **UI Library:** Tailwind CSS + Custom Components
- **Deployment:** AWS S3 + CloudFront CDN
- **Domain:** app.qryti.com

### Backend
- **Framework:** Flask with CORS support
- **Deployment:** AWS EC2 (t2.micro)
- **Proxy:** CloudFlare Tunnel for HTTPS
- **Database:** In-memory (development) / SQLite (planned)

## 📁 Project Structure

```
Qrytiv2/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   ├── assets/          # Static assets
│   │   └── config.js        # Configuration
│   ├── dist/                # Build output
│   └── package.json
├── backend_simple/          # Flask backend
│   ├── app.py              # Main application
│   ├── email_service_enhanced.py
│   ├── requirements.txt
│   └── Dockerfile
├── docs/                   # Documentation
└── scripts/               # Deployment scripts
```

## 🛠️ Development Setup

### Prerequisites
- Node.js 20.18.0+
- Python 3.11+
- AWS CLI configured

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend_simple
pip install -r requirements.txt
python app.py
```

## 🚀 Deployment

### Frontend Deployment
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://app.qryti.com --delete
aws cloudfront create-invalidation --distribution-id E2HCV8NIH27XPX --paths "/*"
```

### Backend Deployment
- Deployed on AWS EC2 instance
- Accessible via CloudFlare Tunnel
- Automatic deployment via user-data scripts

## 🔐 Authentication

### Demo Credentials
- **Admin:** hello@qryti.com / Mandar@123
- **User:** user@demo.qryti.com / demo123
- **Admin Alt:** admin@demo.qryti.com / admin123

## 📊 Features

### Core Functionality
- ✅ User authentication and session management
- ✅ Dashboard with compliance metrics
- ✅ AI model registry and management
- ✅ Gap assessment tools
- ✅ Compliance reporting with PDF export
- ✅ ISO 42001 certification tracking
- ✅ Mobile-responsive design

### Admin Features
- ✅ User management
- ✅ System configuration
- ✅ Analytics and reporting
- ✅ Audit trail

## 🔧 Configuration

### Environment Variables
```bash
# Backend
FLASK_DEBUG=False
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://app.qryti.com

# Frontend
VITE_API_BASE_URL=https://your-backend-url
```

## 📈 Performance

### Current Metrics
- **Bundle Size:** ~264KB (optimizable to <100KB)
- **Load Time:** ~2-3 seconds
- **Lighthouse Score:** 85+ (Performance)

### Optimization Opportunities
- Remove unused UI components (60-70% size reduction)
- Implement code splitting
- Add lazy loading
- Optimize images

## 🔒 Security

### Current Implementation
- CORS protection
- Input validation (basic)
- Session management
- HTTPS enforcement

### Planned Improvements
- Rate limiting
- Input sanitization
- Database encryption
- Audit logging

## 🧪 Testing

### Demo Scenarios
1. **Login Flow:** Use demo credentials to access dashboard
2. **Mobile Testing:** Responsive design on all devices
3. **API Testing:** All endpoints functional
4. **PDF Export:** Compliance reports downloadable

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /health` - API health check

### Core Endpoints
- `GET /api/v1/users/` - User management
- `GET /api/v1/info` - System information
- `GET /api/docs` - API documentation

## 🐛 Known Issues

### Resolved
- ✅ CORS configuration fixed
- ✅ Mobile blank screen resolved
- ✅ API connectivity restored
- ✅ AWS infrastructure optimized

### In Progress
- 🔄 User persistence (in-memory → database)
- 🔄 Client dropdown in project creation
- 🔄 Email service integration
- 🔄 UI/UX improvements

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is proprietary software owned by Qryti.

## 📞 Support

For support and questions:
- **Email:** support@qryti.com
- **Documentation:** [Project Wiki](https://github.com/mandarwaghmare997/Qrytiv2/wiki)
- **Issues:** [GitHub Issues](https://github.com/mandarwaghmare997/Qrytiv2/issues)

---

**Last Updated:** August 3, 2025
**Version:** 2.0.0
**Status:** Production Ready

