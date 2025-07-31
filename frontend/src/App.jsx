import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { 
  Shield, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  BarChart3,
  FileText,
  Users,
  Zap,
  Globe,
  Award,
  ArrowRight,
  Menu,
  X,
  Rocket,
  Target,
  TrendingUp,
  Lock,
  Eye,
  Settings
} from 'lucide-react'
import './App.css'

// Header Component
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="bg-white/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-qryti-green rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">Q</span>
                </div>
                <span className="text-xl font-bold text-gray-900">Qrytiv2</span>
              </div>
            </div>
            <nav className="hidden md:ml-10 md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-qryti-green transition-colors">Features</a>
              <a href="#compliance" className="text-gray-600 hover:text-qryti-green transition-colors">Compliance</a>
              <a href="#dashboard" className="text-gray-600 hover:text-qryti-green transition-colors">Dashboard</a>
              <a href="#pricing" className="text-gray-400 cursor-not-allowed">Pricing</a>
              <a href="#about" className="text-gray-400 cursor-not-allowed">About</a>
            </nav>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" className="text-gray-600 hover:text-qryti-green">
              Sign In
            </Button>
            <Button className="bg-qryti-purple hover:bg-qryti-purple/90 text-white">
              Get Started
            </Button>
          </div>
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t">
            <a href="#features" className="block px-3 py-2 text-gray-600 hover:text-qryti-green">Features</a>
            <a href="#compliance" className="block px-3 py-2 text-gray-600 hover:text-qryti-green">Compliance</a>
            <a href="#dashboard" className="block px-3 py-2 text-gray-600 hover:text-qryti-green">Dashboard</a>
            <div className="px-3 py-4 space-y-2">
              <Button variant="ghost" className="w-full justify-start">Sign In</Button>
              <Button className="w-full bg-qryti-purple hover:bg-qryti-purple/90 text-white">Get Started</Button>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

// Animated Counter Component
const AnimatedCounter = ({ end, duration = 2000, suffix = "" }) => {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime = null
    const animate = (currentTime) => {
      if (startTime === null) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      setCount(Math.floor(progress * end))
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [end, duration])

  return <span className="animate-count-up">{count}{suffix}</span>
}

// Hero Section
const HeroSection = () => {
  return (
    <section className="relative bg-gradient-to-br from-gray-50 to-white py-20 overflow-hidden">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8"
          >
            <Badge className="bg-qryti-green/10 text-qryti-green border-qryti-green/20 mb-4">
              <Rocket className="w-4 h-4 mr-2" />
              Now Supporting ISO 42001 Compliance Framework
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Where AI Meets
              <span className="text-qryti-green"> Governance</span>,
              <br />
              Risk & <span className="text-qryti-blue">Compliance</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Qrytiv2 helps teams implement and manage AI governance frameworks like ISO 42001 — faster, consistently, and at scale.
            </p>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
          >
            <Button size="lg" className="bg-qryti-purple hover:bg-qryti-purple/90 text-white px-8 py-3">
              Request Access
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" className="border-qryti-blue text-qryti-blue hover:bg-qryti-blue hover:text-white px-8 py-3">
              Download eBook
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
          >
            <div className="text-center">
              <div className="text-4xl font-bold text-qryti-blue mb-2">
                <AnimatedCounter end={93} suffix="%" />
              </div>
              <p className="text-gray-600">Faster Compliance</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-qryti-green mb-2">
                24<span className="text-2xl">/7</span>
              </div>
              <p className="text-gray-600">Continuous Monitoring</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-qryti-purple mb-2">
                <AnimatedCounter end={98} suffix="%" />
              </div>
              <p className="text-gray-600">ISO 42001 Ready</p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

// Compliance Dashboard Section
const ComplianceDashboard = () => {
  const stages = [
    { id: 1, name: "Requirements Analysis", status: "completed", progress: 100, description: "AI inventory mapping, risk classification, and stakeholder identification completed with automated documentation." },
    { id: 2, name: "Gap Assessment", status: "completed", progress: 100, description: "Current state analysis against ISO 42001 requirements with prioritized remediation roadmap." },
    { id: 3, name: "Policy Framework", status: "in-progress", progress: 75, description: "AI governance policies, procedures, and controls development with automated compliance validation." },
    { id: 4, name: "Implementation", status: "in-progress", progress: 45, description: "Control deployment, team training, and process integration with continuous monitoring setup." },
    { id: 5, name: "Validation & Testing", status: "pending", progress: 0, description: "Internal audits, control testing, and compliance verification with automated evidence collection." },
    { id: 6, name: "Certification", status: "pending", progress: 0, description: "External audit preparation, certification body engagement, and official ISO 42001 certification." }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-qryti-green text-white'
      case 'in-progress': return 'bg-qryti-orange text-white'
      case 'pending': return 'bg-gray-400 text-white'
      default: return 'bg-gray-400 text-white'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />
      case 'in-progress': return <Clock className="w-4 h-4" />
      case 'pending': return <AlertCircle className="w-4 h-4" />
      default: return <AlertCircle className="w-4 h-4" />
    }
  }

  return (
    <section id="dashboard" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Your ISO 42001 Compliance Dashboard
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Track your AI governance journey with real-time progress monitoring and automated compliance scoring
          </p>
        </div>

        <div className="bg-gray-50 rounded-2xl p-8 mb-12">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">AI Governance Compliance Status</h3>
              <Badge className="bg-qryti-green text-white">
                <Target className="w-4 h-4 mr-2" />
                On Track
              </Badge>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-qryti-green mb-1">
                <AnimatedCounter end={73} suffix="%" />
              </div>
              <p className="text-gray-600">Overall Progress</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stages.map((stage, index) => (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between mb-2">
                      <CardTitle className="text-lg">{stage.id}. {stage.name}</CardTitle>
                      <Badge className={`${getStatusColor(stage.status)} flex items-center gap-1`}>
                        {getStatusIcon(stage.status)}
                        {stage.status === 'completed' ? 'Completed' : 
                         stage.status === 'in-progress' ? 'In Progress' : 'Pending'}
                      </Badge>
                    </div>
                    <Progress value={stage.progress} className="h-2" />
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm">
                      {stage.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

// Features Section
const FeaturesSection = () => {
  const features = [
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Automated Compliance Scoring",
      description: "Real-time ISO 42001 compliance scoring with automated gap analysis, risk assessment, and remediation recommendations powered by AI.",
      color: "text-qryti-blue"
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "AI Model Registry",
      description: "Comprehensive inventory and lifecycle management of all AI models with automated risk scoring, compliance tracking, and governance workflows.",
      color: "text-qryti-green"
    },
    {
      icon: <Eye className="w-8 h-8" />,
      title: "Continuous Risk Monitoring",
      description: "24/7 monitoring of AI model performance, bias detection, ethical compliance with instant alerts and automated incident response.",
      color: "text-qryti-purple"
    },
    {
      icon: <Settings className="w-8 h-8" />,
      title: "Policy Automation",
      description: "Automated policy generation, validation, and enforcement with intelligent document analysis and compliance mapping.",
      color: "text-qryti-orange"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Audit Trail Management",
      description: "Complete audit trail with automated evidence collection, compliance reporting, and certification preparation for ISO 42001.",
      color: "text-qryti-blue"
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "Executive Dashboards",
      description: "C-suite ready compliance scorecards, risk heat maps, and strategic AI governance insights with predictive analytics.",
      color: "text-qryti-green"
    }
  ]

  return (
    <section id="features" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Enterprise-Grade AI Governance Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Built for CISOs, Compliance Heads, and Risk Officers at fast-scaling tech companies
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <Card className="h-full hover:shadow-xl transition-all duration-300 group cursor-pointer">
                <CardHeader>
                  <div className={`${feature.color} mb-4 group-hover:scale-110 transition-transform`}>
                    {feature.icon}
                  </div>
                  <CardTitle className="text-xl mb-2">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// CTA Section
const CTASection = () => {
  return (
    <section className="py-20 bg-gradient-to-r from-qryti-purple to-qryti-blue">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your AI Governance?
          </h2>
          <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
            Join leading tech companies who trust Qrytiv2 for their AI compliance and governance needs.
          </p>
          
          <div className="max-w-md mx-auto bg-white rounded-lg p-6 shadow-xl">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Request Access</h3>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Full Name *</Label>
                <Input id="name" placeholder="Enter your full name" />
              </div>
              <div>
                <Label htmlFor="email">Email Address *</Label>
                <Input id="email" type="email" placeholder="Enter your business email" />
              </div>
              <div>
                <Label htmlFor="company">Organization Name *</Label>
                <Input id="company" placeholder="Enter your organization" />
              </div>
              <Button className="w-full bg-qryti-purple hover:bg-qryti-purple/90 text-white">
                Request Access
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

// Footer
const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-qryti-green rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">Q</span>
              </div>
              <span className="text-xl font-bold">Qrytiv2</span>
            </div>
            <p className="text-gray-400 mb-4">
              Professional ISO 42001 compliance management platform for AI governance and risk management.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Compliance</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Dashboard</a></li>
              <li><a href="#" className="hover:text-white transition-colors">API</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">About</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Guides</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2025 Qrytiv2. Built with ❤️ by the Qryti Dev Team. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

// Main App Component
function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white">
        <Header />
        <main>
          <HeroSection />
          <ComplianceDashboard />
          <FeaturesSection />
          <CTASection />
        </main>
        <Footer />
      </div>
    </Router>
  )
}

export default App

