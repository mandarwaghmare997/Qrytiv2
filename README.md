# Qrytiv2 - ISO 42001 Compliance Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)

A lightweight, open-source compliance management platform specifically designed for ISO 42001 (Artificial Intelligence Management Systems) compliance. Built by the Qryti Dev Team.

## 🎯 Features

- **Flexible Compliance Journey**: Start at any stage, skip non-applicable sections with justification
- **Professional Reporting**: Generate audit-ready PDF reports and compliance certificates
- **Multi-User Support**: Role-based access control with admin and user roles
- **Evidence Management**: Upload and track evidence per control with metadata validation
- **Real-time Scoring**: 0-100% compliance scoring based on completed stages and controls
- **Audit Trail**: Comprehensive activity logging for compliance purposes
- **Multiple Deployment Options**: Windows, Docker, and AWS deployment support

## 🏗️ Architecture

- **Backend**: Python FastAPI with SQLite/PostgreSQL
- **Frontend**: React 18 with Vite and Tailwind CSS
- **Authentication**: JWT-based with email domain validation
- **Storage**: Local filesystem or S3-compatible storage
- **Reporting**: WeasyPrint for professional PDF generation

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/mandarwaghmare997/Qrytiv2.git
   cd Qrytiv2
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m app.main
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Deployment

```bash
docker-compose up -d
```

### Windows Installation

Download the latest installer from the [Releases](https://github.com/mandarwaghmare997/Qrytiv2/releases) page.

## 📋 ISO 42001 Compliance Stages

1. **Requirements Analysis** - Define organizational context and AI governance requirements
2. **Gap Assessment** - Identify gaps between current state and ISO 42001 requirements
3. **Policy Framework** - Develop and implement AI governance policies
4. **Implementation** - Execute controls and processes
5. **Validation & Testing** - Verify implementation effectiveness
6. **Certification** - Prepare for and undergo certification audit

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./qrytiv2.db  # or postgresql://...

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
STORAGE_TYPE=local  # or s3
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1

# Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password

# Slack Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## 📚 Documentation

- [API Documentation](docs/api/README.md)
- [User Guide](docs/user/README.md)
- [Administrator Guide](docs/admin/README.md)
- [Deployment Guide](deployment/README.md)

## 🧪 Testing

```bash
# Backend Tests
cd backend
pytest

# Frontend Tests
cd frontend
npm test

# End-to-End Tests
npm run test:e2e
```

## 🚢 Deployment

### AWS Deployment

See [AWS Deployment Guide](deployment/aws/README.md) for detailed instructions.

### Docker Deployment

See [Docker Deployment Guide](deployment/docker/README.md) for detailed instructions.

### Windows Deployment

See [Windows Deployment Guide](deployment/windows/README.md) for detailed instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check our comprehensive [documentation](docs/)
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/mandarwaghmare997/Qrytiv2/issues)
- **Email**: Contact us at dev@qryti.com

## 🏢 About Qryti

Qrytiv2 is developed by the Qryti Dev Team as part of our commitment to making compliance management accessible and affordable for organizations of all sizes.

Visit [qryti.com](https://qryti.com) for more information about our compliance solutions.

---

**Built with ❤️ by the Qryti Dev Team**

