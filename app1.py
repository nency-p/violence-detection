from flask import Flask, request, jsonify, render_template_string
import os
import webbrowser
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folder to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"csv", "jpg", "jpeg", "png", "webp", "mp4", "avi", "mov", "webm"}

STREAMLIT_URL = "http://localhost:8501"  # Streamlit dashboard URL

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    # Keep only alphanumeric characters, dots, underscores, and hyphens
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename

# Your complete HTML page with the new violence detection interface
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeVision - Login & Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            transition: background 0.5s ease;
        }

        /* --- Login/Register Styles --- */
        .auth-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 450px;
            padding: 40px;
            position: relative;
            transition: all 极端的.5s ease;
        }
        .auth-container::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .logo p { color: #666; font-size: 0.95rem; }
        .auth极端的-tabs { display: flex; margin-bottom: 30极端的px; background: #f8f9fa; border-radius: 12px; padding: 4px; }
        .tab-btn {
            flex: 1;
            padding: 12px;
            background: none;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            color: #666;
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .auth-form { display: none; }
        .auth-form.active { display: block; animation: fadeIn 0.5s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .form-group { margin-bottom: 20px; position: relative; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; font-size: 0.9rem; }
        .form-group input {
            width: 100%; padding: 14px 16px; border: 2px solid #e9ecef;
            border-radius: 10px; font-size: 1rem; transition: all 0.3s ease; background: #fff;
        }
        .form-group input:focus {
            outline: none; border-color: #667eea;极端的 box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .form-group i { position: absolute; right: 16px; top: 50%; transform: translateY(-50%); color: #999; margin-top: 12px; cursor: pointer; }
        .submit-btn {
            width: 100%; padding: 16px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease;
        }
        .submit-btn:hover { transform: translateY(-2px); }
        .forgot-password { text-align: center; margin-top: 20px; }
        .forgot-password a { color: #667eea; text-decoration: none; font-size: 0.9rem; }
        .divider { text-align: center; margin: 25px 0; position: relative; color: #999; font-size: 0.9rem; }
        .divider::before { content: ''; position: absolute; top: 50%; left极端的: 0; right: 0; height: 1px; background: #e9ecef; z-index: 1; }
        .divider span { background: rgba(255,255,255,0.95); padding: 0 15px; position: relative; z-index: 2; }
        .social-login { display: flex; gap: 15px; margin-top: 20px; }
        .social-btn {
            flex: 1; padding: 12px; border: 2px solid #极端的e9ecef; background: white; border-radius: 10px;
            cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; font-weight: 600;
        }
        .social-btn:hover { border-color: #667eea; background: #f8f9ff; }
        .terms { margin-top: 20px; font-size: 0.85rem; color: #666; text-align: center; }
        .terms a { color: #667eea; text-decoration: none; }
        .success-message { background: #d4edda; color: #155724; padding: 12px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #c3e6cb; display: none; }

        /* --- Dashboard Styles --- */
        .dashboard {
            display: none;
            width: 100%;
            height: 100vh;
            position: absolute;
            top: 0; left: 0;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #0c0c0c 100%);
            color: #fff;
            padding: 40px;
            overflow-y: auto;
            animation: fadeIn 0.5s ease;
        }
        .dashboard.active { display: block; }

        .background-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 20% 30%, rgba(255,0,0,0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 70%, rgba(0,100,255,极端的0.1) 0%, transparent 50%),
                        linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.03) 50%, transparent 70%);
            animation: backgroundShift 10s ease-in-out infinite;
            z-index: 0;
        }
        @keyframes backgroundShift {
            0%, 100% { transform: translate极端的X(0) translateY(0); }
            50% { transform: translateX(20px) translateY(-20px); }
        }

        .security-grid {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: linear-gradient(rgba(0,255,255,0.1) 极端的1px, transparent 1px),
                              linear-gradient(90deg, rgba(0,255,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: gridPulse 4s ease-in-out infinite;
            opacity: 0.3;
            z-index: 1;
        }
        @keyframes gridPulse { 0%,100%{opacity:0.2;}50%{opacity:0.4;} }

        .floating-elements { position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:2; }
        .floating-element {
            position: absolute; width: 4px; height: 4px;
            background: rgba(0,255,255,0.6); border-radius:50%;
            animation: float 8s linear infinite;
        }
        @keyframes float { 0%{transform:translateY(100vh) translateX(0) scale(0);opacity:0;}
                           10%{opacity:1;transform:scale极端的(1);}
                           90%{opacity:1;}
                           100%{transform:translateY(-100vh) translateX(100px) scale(0);opacity:0;} }

        .dashboard-content { position: relative; z-index: 10; text-align:center; }
        .dashboard .logo { font-size:3.5em; font-weight:800; background: linear-gradient(135deg,#00ffff,#0080ff,#ffffff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:20px; text-shadow:0 0 30px rgba(0,255,255,0.3);}
        .dashboard .title { font-size:3.2em; font-weight:700; color:#fff; margin-bottom:30px; line-height:1.2; text-shadow:0 2px 10px rgba(0,0,0,0.5);}
        .dashboard .subtitle { font-size:1.3em; color:#b0b0b0; margin-bottom:40px; line-height:1.6; max-width:600px; margin-left:auto;margin-right:auto;}
        .features { display:flex; justify-content:center; gap:40px; margin-bottom:50px; flex-wrap:wrap; }
        .feature { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border:1px solid rgba(0,255,255,0.2); padding:25px; border-radius:15px; transition:all 0.3s ease; min-width:200px;}
        .feature:hover { transform:translateY(-10px); background: rgba(255,255,255,0.1); border-color: rgba(0,255,255,0.4); box-shadow:0 10px 30px rgba(0,255,255,0.2);}
        .feature-icon { font-size:2.5em; margin-bottom:15px; color:#00ffff; }
        .feature-title { font-size:1.1em; font-weight:600; color:#fff; margin-bottom:10px; }
        .feature-desc { font-size:0.9极端的em; color:#b0b0b0; line-height:1.4; }
        .get-started-btn { background:linear-gradient(135deg,#ff6极端的b6b,#ee5a24,#ff6b6b); color:white; font-size:1.4em; font-weight:700; padding:20px 50px; border:none; border-radius:50px; cursor:pointer; text-transform:uppercase; letter-spacing:2px; position:relative; overflow:hidden; box-shadow:0 10px 30px rgba(极端的255,107,107,0.3); animation:buttonPulse 2s ease-in-out infinite; }
        @keyframes buttonPulse { 0%,100%{box-shadow:0 10px 30px rgba(255,107,107,0.3);transform:scale(1);}50%{box-shadow:0 15px 40px rgba(255,107,107,0.5);transform:scale(1.05);} }
        
        /* --- Violence Detection Styles --- */
        .violence-detection-container {
            display: none;
            width: 100%;
            min-height: 100vh;
            position: absolute;
            top: 0; left: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #ffffff;
            padding: 40px 20px;
            overflow-y: auto;
            animation: fadeIn 0.5s ease;
        }
        .violence-detection-container.active { display: block; }
        
        .violence-header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .violence-title {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #00ffff, #0080ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .violence-subtitle {
            font-size: 1.2em;
            color: #b0b0b0;
            font-weight: 300;
        }
        
        .upload-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }

        .upload-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(0, 255, 255, 0.2);
            border-radius: 20px;
            padding: 30px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .upload-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90极端的deg, transparent, rgba(0, 255, 255, 0.1), transparent);
            transition: left 0.5s;
        }

        .upload-card:hover {
            transform: translateY(-5px);
            border-color: rgba(0, 255, 255, 0.4);
            box-shadow: 0 15px 40px rgba(0, 255, 255, 0.15);
        }

        .upload-card:hover::before {
            left: 100%;
        }

        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }

        .card-icon {
            font-size: 2.5em;
            margin-right: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 70px;
            height: 70px;
        }

        .card-title {
            font-size: 1.5em;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 5px;
        }

        .card-subtitle {
            font-size: 0.9em;
            color: #00ffff;
            font-weight: 300;
        }

        .card-description {
            margin-bottom: 25px;
        }

        .main-desc {
            font-size: 1.1em;
            color: #e0e0e0;
            margin-bottom: 15px;
            line-height: 1.5;
        }

        .features-list {
            list-style: none;
            padding-left: 0;
        }

        .features-list li {
            color: #b0b0b0;
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
            font-size: 0.95em;
            line-height: 1.4;
        }

        .features-list li::before {
            content: '•';
            color: #00ffff;
            position: absolute;
            left: 0;
            font-size: 1.2em;
        }

        .upload-button {
            width: 100%;
            background: linear-gradient(135deg, #00ffff, #0080ff);
            color: #ffffff;
            border: none;
            padding: 15px 20px;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }

        .upload-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 128, 255, 0.4);
        }

        .upload-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .upload-button:hover::before {
            left: 100%;
        }

        .file-input {
            display: none;
        }

        .info-section {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }

        .info-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #00ffff;
        }

        .info-text {
            color: #b0b0b0;
            line-height: 1.6;
            margin-bottom: 15px;
        }

        .back-button {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 100;
        }
        
        .back-button:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(-5px);
        }
        
        .status-message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.1em;
            display: none;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .status-success {
            background-color: rgba(0, 255, 0, 0.1);
            color: #00ff00;
            border: 1px solid rgba(0, 255, 0, 0.3);
        }
        
        .status-error {
            background-color: rgba(255, 0, 0, 0.1);
            color: #ff5555;
            border: 1px solid rgba(255, 0, 0, 0.3);
        }
        
        .status-processing {
            background-color: rgba(255, 165, 0, 0.1);
            color: #ffaa00;
            border: 1px solid rgba(255, 165, 0, 0.3);
        }
        
        @media (max-width: 768px) {
            .upload-grid {
                grid-template-columns: 1fr;
            }
            
            .violence-title {
                font-size: 2em;
            }
            
            .upload-card {
                padding: 20px;
            }
            
            .card-icon {
                width: 60px;
                height: 60px;
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <!-- Login/Register Form -->
    <div class="auth-container" id="authContainer">
        <div class="logo">
            <h1><i class="fas fa-shield-alt"></i> SafeVision</h1>
            <p>Login Page</p>
        </div>

        <div class="auth-tabs">
            <button class="tab-btn active" onclick="switchTab('login')">Login</button>
            <button class="tab-btn" onclick="switchTab('register')">Register</button>
        </div>

        <div class="success-message" id="successMessage">
            <极端的i class="fas fa-check-circle"></i> Account created successfully! Please login.
        </div>

        <form class="auth-form active" id极端的="loginForm">
            <div class="form-group">
                <label for="loginEmail">Email Address</label>
                <input type="email" id="loginEmail" name="email" required>
                <i class="fas fa-envelope"></i>
            </div>
            <div class="form-group">
                <label for="loginPassword">Password</label>
                <input type="password" id="loginPassword" name="password" required>
                <i class="fas fa-eye" onclick="togglePassword('loginPassword', this)"></i>
            </div>
            <button type="submit" class="submit-btn">
                <i class="fas fa-sign-in-alt"></i> Login
            </button>
            <div class="forgot-password">
                <a href="#" onclick="showForgotPassword()">Forgot Password?</a>
            </div>
        </form>

        <form class="auth-form" id="registerForm">
            <div class="form-group">
                <label for="fullName">Full Name</label>
                <input type="text" id="fullName" name="fullName" required>
                <i class="fas fa-user"></i>
            </div>
            <div class="form-group">
                <label for="organization">Organization</label>
                <input type="text" id="organization" name="organization" placeholder="School, Office, Mall, etc." required>
                <i class="fas fa-building"></i>
            </div>
            <div class="form-group">
                <label for="registerEmail">Email Address</label>
                <input type="email" id="registerEmail" name="email" required>
                <i class="fas fa-envelope"></i>
            </div>
            <div class="form-group">
                <label for="registerPassword">Password</label>
                <input type="password" id="registerPassword" name="password" required>
                <i class="fas fa-eye" onclick="togglePassword('registerPassword', this)"></极端的i>
            </div>
            <div class="form-group">
                <label for="confirmPassword">Confirm Password</label>
                <input type="password" id="confirmPassword" name="confirmPassword" required>
                <i class="fas fa-eye" onclick="togglePassword('confirmPassword', this)"></i>
            </div>
            <button type="submit" class极端的="submit-btn">
                <i class="fas fa-user-plus"></i> Register
            </button>
            <div class="terms">
                By creating an account, you agree to the <a href="#">Terms</a> and <a href="#">Privacy Policy</a>
            </div>
        </form>
    </div>

    <!-- Dashboard -->
    <div class="dashboard" id="dashboard">
        <div class="background-overlay"></div>
        <div class="security-grid"></div>
        <div class="floating-elements"></div>
        <div class="dashboard-content">
            <div class="极端的logo">SafeGuard AI</div>
            <div class="title">Real-Time Violence Detection</div>
            <div class="subtitle">Harness AI to detect and prevent violent incidents in real-time. Instant alerts and monitoring for enhanced security.</div>
            <div class="features">
                <div class="feature"><div class="feature-icon">🛡️</div><div class="feature-title">Real-Time Monitoring</div><div class="feature-desc">24/7 surveillance with instant threat detection</div></div>
                <div class="feature"><div class="feature-icon">🤖</div><div class="feature-title">AI-Powered Analysis</div><div class="feature-desc">Advanced machine learning algorithms</div></div>
                <div class="feature"><div class="feature-icon">⚡</div><div class="feature-title">Instant Alerts</div><div class="feature-desc">Immediate notifications for rapid response</div></div>
            </div>
            <button class="get-started-btn" id="getStartedBtn">Get Started</button>
        </div>
    </div>

    <!-- Violence Detection Interface -->
    <div class="violence-detection-container" id="violenceDetectionContainer">
        <button class="back-button" id="backToDashboard">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
        </button>
        
        <div class="violence-header">
            <h1 class="violence-title">Violence Detection System</h1>
            <p class="violence-subtitle">Upload your files or start real-time analysis</p>
        </div>

        <div class="upload-grid">
            <!-- CSV Upload Card -->
            <div class="upload-card">
                <div class="card-header">
                    <div class="card-icon">📊</div>
                    <div>
                        <div class="card-title">CSV Upload</div>
                        <div class="card-subtitle">Data Analysis</div>
                    </div>
                </div>
                <div class="card-description">
                    <div class="main-desc">Upload CSV files containing incident data for comprehensive analysis and model training.</div>
                    <ul class="features-list">
                        <li>Batch processing of historical incident data</li>
                        <li>Statistical analysis and pattern recognition</li>
                        <li>Model training data preparation</li>
                        <li>Supports multiple CSV formats and encodings</li>
                        <li>Automatic data validation and cleaning</li>
                    </ul>
                </div>
                <input type="file" id="csv-upload" class="file-input" accept=".csv" multiple>
                <button class="upload-button" onclick="document.getElementById('csv-upload').click()">
                    Upload CSV Files
                </button>
            </div>

            <!-- Image Upload Card -->
            <div class="upload-card">
                <div class="card-header">
                    <div class="card-icon">🖼️</div>
                    <div>
                        <div class="card-title">Image Upload</div>
                        <div class="card-subtitle">Single Frame Analysis</div>
                    </div>
                </div>
                <div class="card-description">
                    <div class="main-desc">Upload images for violence detection and threat assessment analysis.</div>
                    <ul class="features-list">
                        <li>Support for JPG, PNG, WEBP formats</li>
                        <li>Advanced computer vision algorithms</li>
                        <li>Object and behavior recognition</li>
                        <li>Confidence scoring and threat levels</li>
                        <li>Detailed analysis reports with annotations</li>
                    </ul>
                </div>
                <input type="file" id="image-upload" class="file-input" accept="image/*" multiple>
                <button class="upload-button" onclick="document.getElementById('image-upload').click()">
                    Upload Images
                </button>
            </div>

            <!-- Video Upload Card -->
            <div class="upload-card">
                <div class="card-header">
                    <div class="card-icon">🎥</div>
                    <div>
                        <div class="card-title">Video Upload</div>
                        <div class="card-subtitle">Temporal Sequence Analysis</div>
                    </div>
                </div>
                <div class="card-description">
                    <div class="main-desc">Upload video files for comprehensive temporal analysis and incident detection.</div>
                    <ul class="features-list">
                        <li>Support for MP4, AVI, MOV, WebM formats</li>
                        <极端的li>Frame-by-frame violence detection</li>
                        <li>Timeline-based incident mapping</li>
                        <li>Automatic highlight generation</li>
                        <li>Progressive analysis with real-time updates</li>
                    </ul>
                </div>
                <input type="file" id="video-upload" class="file-input" accept="video/*" multiple>
                <button class="upload-button" onclick="document.getElementById('video-upload').click()">
                    Upload Videos
                </button>
            </div>
        </div>

        <div class="info-section">
            <div class="info-title">System Capabilities:</div>
            <div class="info-text">
                Our advanced violence detection system combines cutting-edge machine learning with real-time processing capabilities. The system can analyze multiple data types simultaneously and provides comprehensive threat assessment with detailed reporting.
            </div>
            <ul class="features-list">
                <li>Multi-modal analysis (video, audio, metadata)</li>
                <li>Real-time processing with sub-second response times</li>
                <li>Scalable architecture supporting multiple concurrent streams</li>
                <li>Advanced AI models trained on diverse datasets</li>
                <li>Customizable alert thresholds and notification systems</li>
                <li>Integration with existing security infrastructure</li>
            </ul>
        </div>

        <div id="statusMessage" class="status-message"></div>
    </div>

    <script>
        // Tab switch
        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
            document.getElementById(tab + 'Form').classList.add('active');
            document.getElementById('successMessage').style.display = 'none';
        }

        // Password toggle
        function togglePassword(inputId, icon) {
            const input = document.getElementById(inputId);
            if(input.type === 'password'){ input.type='text'; icon.classList.replace('fa-eye','fa-eye-slash'); }
            else{ input.type='password'; icon.classList.replace('fa-eye-slash','fa-eye'); }
        }

        function showForgotPassword(){ alert('This is a login page. Forgot password will be implemented in backend.'); }

        // Dummy login credentials
        const dummyEmail = 'nency07@gmail.com';
        const dummyPassword = 'password123';

        document.getElementById('loginForm').addEventListener('submit', function(e){
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            if(email === dummyEmail && password === dummyPassword){
                // Show dashboard
                document.getElementById('authContainer').style.display = 'none';
                document.getElementById('dashboard').classList.add('active');
                // Add floating elements
                for(let i=0;i<50;i++){
                    const el = document.createElement('div');
                    el.className='floating-element';
                    el.style.left = Math.random()*100+'%';
                    el.style.animationDelay = Math.random()*8+'s';
                    document.querySelector('.floating-elements').appendChild(el);
                }
            } else{
                alert('Invalid credentials! Use:\\nEmail: nency07@gmail.com\\nPassword: password123');
            }
        });

        document.getElementById('registerForm').addEventListener('submit', function(e){
            e.preventDefault();
            document.getElementById('successMessage').style.display = 'block';
            switchTab('login');
        });

        // File upload functionality
        const getStartedBtn = document.getElementById('getStartedBtn');
        const violenceDetectionContainer = document.getElementById('violenceDetectionContainer');
        const backToDashboard = document.getElementById('backToDashboard');
        const statusMessage = document.getElementById('statusMessage');
        const csvUpload = document.getElementById('csv-upload');
        const imageUpload = document.getElementById('image-upload');
        const videoUpload = document.getElementById('video-upload');

        // Setup file input event listeners
        [csvUpload, imageUpload, videoUpload].forEach(input => {
            input.addEventListener('change', function(event) {
                const files = event.target.files;
                if (files.length > 0) {
                    const type = input.id.split('-')[0].charAt(0).toUpperCase() + input.id.split('-')[0].slice(1);
                    uploadFiles(files, type);
                }
            });
        });

        // Upload files to Flask backend
        function uploadFiles(files, type) {
            const formData = new FormData();
            
            for (let i = 0; i < files.length; i++) {
                formData.append('file', files[i]);
            }
            
            // Show processing status
            showStatus(`Processing your ${type.toLowerCase()} files...`, 'processing');
            
            // Send to Flask backend
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus(`${type} files uploaded successfully! Analysis will begin shortly.`, 'success');
                    
                    // Reset file inputs
                    document.getElementById(`${type.toLowerCase()}-upload`).value = '';
                } else {
                    showStatus('Upload failed: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                showStatus('Error uploading files. Make sure the Flask server is running on port 5000.', 'error');
                console.error('Upload error:', error);
            });
        }

        // Show status message
        function showStatus(message, type) {
            statusMessage.textContent = message;
            statusMessage.className = 'status-message';
            
            switch(type) {
                case 'success':
                    statusMessage.classList.add('status-success');
                    break;
                case 'error':
                    statusMessage.classList.add('status-error');
                    break;
                case 'processing':
                    statusMessage.classList.add('status-processing');
                    break;
            }
            
            statusMessage.style.display = 'block';
            
            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    statusMessage.style.display = 'none';
                }, 5000);
            }
        }

        // Navigation between dashboard and violence detection
        getStartedBtn.addEventListener('click', function() {
            document.getElementById('dashboard').classList.remove('active');
            document.getElementById('violenceDetectionContainer').classList.add('active');
        });

        backToDashboard.addEventListener('click', function() {
            document.getElementById('violenceDetectionContainer').classList.remove('active');
            document.getElementById('dashboard').classList.add('active');
            // Reset status message
            statusMessage.style.display = 'none';
        });

        // Add drag and drop functionality
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
        });
    </script>
</body>
</html>
"""

# --------------------- Routes ---------------------

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify(success=False, error="No file part in request")

    file = request.files["file"]
    if file.filename == "":
        return jsonify(success=False, error="No file selected")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        return jsonify(success=True, filename=filename)
    else:
        return jsonify(success=False, error="Invalid file type. Allowed types: CSV, JPG, JPEG, PNG, WEBP, MP4, AVI, MOV, WebM")

# --------------------- Run App ---------------------

if __name__ == "__main__":
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Optional: Automatically open in browser
    webbrowser.open_new_tab("http://127.0.0.1:5000")
    app.run(debug=True, port=5000)