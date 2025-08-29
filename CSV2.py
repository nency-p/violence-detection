from flask import Flask, request, jsonify, render_template_string
import os
import webbrowser

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folder to store uploaded CSVs
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"csv"}

STREAMLIT_URL = "http://localhost:8501"  # Streamlit dashboard URL

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    # Keep only alphanumeric characters, dots, underscores, and hyphens
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename

# Your HTML page content (the entire HTML from your file)
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
            transition: all 0.5s ease;
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
        .auth-tabs { display: flex; margin-bottom: 30px; background: #f8f9fa; border-radius: 12px; padding: 4px; }
        .tab-btn {
            flex: 1;
            padding: 12px;
            background: none;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            color: 666;
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
            outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
        .divider::before { content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: #e9ecef; z-index: 1; }
        .divider span { background: rgba(255,255,255,0.95); padding: 0 15px; position: relative; z-index: 2; }
        .social-login { display: flex; gap: 15px; margin-top: 20px; }
        .social-btn {
            flex: 1; padding: 12px; border: 2px solid #e9ecef; background: white; border-radius: 10px;
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
                        radial-gradient(circle at 80% 70%, rgba(0,100,255,0.1) 0%, transparent 50%),
                        linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.03) 50%, transparent 70%);
            animation: backgroundShift 10s ease-in-out infinite;
            z-index: 0;
        }
        @keyframes backgroundShift {
            0%, 100% { transform: translateX(0) translateY(0); }
            50% { transform: translateX(20px) translateY(-20px); }
        }

        .security-grid {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: linear-gradient(rgba(0,255,255,0.1) 1px, transparent 1px),
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
                           10%{opacity:1;transform:scale(1);}
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
        .feature-desc { font-size:0.9em; color:#b0b0b0; line-height:1.4; }
        .get-started-btn { background:linear-gradient(135deg,#ff6b6b,#ee5a24,#ff6b6b); color:white; font-size:1.4em; font-weight:700; padding:20px 50px; border:none; border-radius:50px; cursor:pointer; text-transform:uppercase; letter-spacing:2px; position:relative; overflow:hidden; box-shadow:0 10px極端30px rgba(255,107,107,0.3); animation:buttonPulse 2s ease-in-out infinite; }
        @keyframes buttonPulse { 0%,100%{box-shadow:0 10px 30px rgba(255,107,107,0.3);transform:scale(1);}50極端{box-shadow:0 15px 40px rgba(255,107,107,0.5);transform:scale(1.05);} }
        
        /* --- CSV Upload Styles --- */
        .csv-upload-container {
            display: none;
            width: 100%;
            min-height: 100vh;
            position: absolute;
            top: 0; left: 0;
            background: linear-gradient(135極端deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #ffffff;
            padding: 40px 20px;
            overflow-y: auto;
            animation: fadeIn 0.5s ease;
        }
        .csv-upload-container.active { display: flex; align-items: center; justify-content: center; }
        
        .csv-header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .csv-title {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #00ffff, #0080ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
極端        .csv-subtitle {
            font-size: 1.2em;
            color: #b0b0b0;
            font-weight: 300;
        }
        
        .upload-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(0, 255, 255, 0.2);
            border-radius: 20px;
            padding: 40px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            max-width: 600px;
            width: 100%;
        }
        
        .upload-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 極端0.1), transparent);
            transition: left 極端0.5s;
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
            justify-content: center;
            margin-bottom: 30px;
        }
        
        .card-icon {
            font-size: 4em;
            margin-right: 20px;
           極端 padding: 20px;
            background: linear-gradient(135deg, #00ffff, #0080ff);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100px;
            height: 100px;
            box-shadow: 0 10px 30px rgba(0, 255, 255, 0.3);
        }
        
        .card-title-section {
            text-align: left;
        }
        
        .card-title {
            font-size: 2em;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 8px;
        }
        
        .card-subtitle {
            font-size: 1極端.1em;
            color: #00ffff;
            font-weight: 300;
        }
        
        .card-description {
            margin-bottom: 35px;
            text-align: center;
        }
        
        .main-desc {
            font-size: 1.2em;
            color: #e0e0極端e0;
            margin-bottom: 25px;
            line-height: 1.6;
        }
        
        .features-list {
            list-style: none;
            padding: 0;
            text-align: left;
            display: inline-block;
        }
        
        .features-list li {
            color: #b0b0b0;
            margin-bottom: 12px;
            padding-left: 25px;
            position: relative;
            font-size: 1em;
            line-height: 1.5;
        }
        
        .features-list li::before {
            content: '✓';
            color: #00ffff;
            position: absolute;
            left: 0;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .upload-button {
            width: 100%;
            background: linear-gradient(135deg, #00ffff, #0080ff);
            color: #ffffff;
            border: none;
            padding: 18px 30px;
            border-radius: 15px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }
        
        .upload-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(0, 128, 255, 0.4);
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
        
        .drag-drop-zone {
            border: 2px dashed rgba(0, 255, 255, 0.3);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            text-align: center;
            transition: all 0.3s極端 ease;
            background: rgba(0, 255, 255, 0.02);
        }
        
        .drag-drop-zone.drag-over {
            border-color: rgba(0, 255, 255, 0.6);
            background: rgba(0, 255, 255, 0.05);
            transform: scale(1.02);
        }
        
        .drag-text {
            color: #b0b0b0;
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        
        .or-divider {
            text-align: center;
            margin: 30px 0;
            position: relative;
            color: #888;
            font-size: 1.1em;
        }
        
        .or-divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(136, 136, 136, 0.5), transparent);
        }
        
        .or-divider span {
            background: linear-gradient(135deg, #1極端a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 0 20px;
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
極端           display: none;
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
            background-color: rgba(255, 165, 0, 0.極端1);
            color: #ffaa00;
            border: 極端1px solid rgba(255, 165, 0, 0.3);
        }
        
        .dashboard-button {
            margin-top: 20px;
            background: linear-gradient(135deg, #f12711, #f5af19);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .dashboard-button:hover {
            background: linear-gradient(135deg, #ff512f, #f09819);
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .csv-title {
                font-size: 2em;
            }
            
            .upload-card {
                padding: 30px 20px;
            }
            
            .card-header {
                flex-direction: column;
                text-align: center;
            }
            
            .card-icon {
                margin-right: 0;
                margin-bottom: 20px;
                width: 80px;
                height: 80px;
                font-size: 3em;
            }
            
            .card-title {
                font-size: 1.8em;
                text-align: center;
            }
            
            .card-title-section {
                text-align: center;
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

        <div class="auth極端-tabs">
            <button class="tab-btn active" onclick="switchTab('login')">Login</button>
            <button class="tab-btn" onclick="switchTab('register')">Register</button>
        </div>

        <div class="success-message" id="successMessage">
            <i class="fas fa-check-circle"></i> Account created successfully! Please login.
        </div>

        <form class="auth-form active" id="loginForm">
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
                <i極端 class="fas fa-sign-in-alt"></i> Login
            </button>
            <div class="forgot-password">
                <a href="#" onclick="showForgotPassword()">Forgot Password?</a>
            </div>
        </form>

        <form class="auth-form" id="registerForm">
            <div class極端="form-group">
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
                <i class="fas fa-eye" onclick="togglePassword('registerPassword', this)"></i>
            </div>
            <div class="form-group">
                <label for="confirmPassword">Confirm Password</label>
                <input type="password" id="confirmPassword" name="confirmPassword" required>
                <i class="fas fa-eye" onclick="togglePassword('confirmPassword', this)"></i>
            </div>
            <button type="submit" class="submit-btn">
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
            <div class="logo">SafeGuard AI</div>
            <div class="title">Real-Time Violence Detection</div>
            <div class="subtitle">Harness AI to detect and prevent violent incidents in real-time. Instant alerts and monitoring for enhanced security.</div>
            <div class="features">
                <div class="feature"><div class="feature-icon">🛡️</div><div class="feature-title">Real-Time Monitoring</div><div class="feature-desc">24/7 surveillance with instant threat detection</div></div>
                <div class="feature"><div class="feature-icon">🤖</div><div class="feature-title">AI-Powered Analysis</div><div class="feature-desc">Advanced machine learning algorithms</div></div>
                <div class="feature"><div class="feature-icon">⚡</div><div class極端="feature-title">Instant Alerts</div><div class="feature-desc">Immediate notifications for極端 rapid response</極端div></div>
            </div>
            <button class="get-started-btn" id="getStartedBtn">Get Started</button>
        </div>
    </div>

    <!-- CSV Upload Interface -->
    <div class="csv-upload-container" id="csvUploadContainer">
        <button class="back-button" id="backToDashboard">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
        </button>
        
        <div class="container">
            <div class="csv-header">
                <h1 class="csv-title">Violence Detection System</h1>
                <p class="csv-subtitle">Upload your CSV files for analysis</p>
            </div>

            <div class="upload-card" id="uploadCard">
                <div class="card-header">
                    <div class="card-icon">📊</div>
                    <div class="card-title-section">
                        <div class="card-title">CSV File Upload</div>
                        <div class="card-subtitle">Data Analysis & Training</div>
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
                        <li>Real-time processing極端 status updates</li>
                    </ul>
                </div>

                <div class="drag-drop-zone" id="dragDropZone">
                    <div class="drag-text">Drag and drop your CSV files here</div>
                    <div style="color: #666; font-size: 0.9em;">Supported formats: .csv files up to 50MB</極端div>
                </div>

                <div class="or-divider">
                    <span>OR</span>
                </div>

                <input type="file" id="csv-upload" class="file-input" accept=".csv" multiple>
                <button class="upload-button" id="uploadButton">
                    Browse & Upload CSV Files
                </button>
                
                <div id="statusMessage" class="status-message"></div>
                
                <button class="dashboard-button" id="openDashboardBtn" style="display: none;">
                    📊 Open Analysis Dashboard
                </button>
            </div>
        </div>
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
        function socialLogin(provider){ alert(provider + ' login clicked.'); }

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
                    el.style.animationDelay = Math.random()*8+'極端s';
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

        // CSV Upload functionality
        const dragDropZone = document.getElementById('dragDropZone');
        const uploadCard = document.getElementById('uploadCard');
        const getStartedBtn = document.getElementById('getStartedBtn');
        const csvUploadContainer = document.getElementById('csvUploadContainer');
        const backToDashboard = document.getElementById('backToDashboard');
        const uploadButton = document.getElementById('uploadButton');
        const fileInput = document.getElementById('csv-upload');
        const statusMessage = document.getElementById('statusMessage');
        const openDashboardBtn = document.getElementById('openDashboardBtn');

        // Show file dialog when upload button is clicked
        uploadButton.addEventListener('click', function() {
            fileInput.click();
        });

        // Handle file selection
        fileInput.addEventListener('change', function(event) {
            const files = event.target.files;
            if (files.length > 0) {
                uploadFiles(files);
            }
        });

        // Upload files to Flask backend
        function uploadFiles(files) {
            const formData = new FormData();
            
            for (let i = 0; i < files.length; i++) {
                formData.append('file', files[i]);
            }
            
            // Show processing status
            showStatus('Processing your files...', 'processing');
            
            // Send to Flask backend
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('Files uploaded successfully!', 'success');
                    // Show dashboard button
                    openDashboardBtn.style.display = 'block';
                    
                    // Simulate processing feedback
                    const button = document.querySelector('.upload-button');
                    const originalText = button.textContent;
                    button.textContent = 'Processing...';
                    button.style.background = 'linear-gradient(135deg, #ff9500, #ff6b00)';
                    
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.style.background = 'linear-gradient(135deg, #00ffff, #0080ff)';
                    }, 2000);
                } else {
                    showStatus('Upload failed: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                showStatus('Error uploading files: ' + error.message, 'error');
                console.error('Upload error:', error);
            });
        }
         openDashboardBtn.addEventListener('click', function() {
            window.open('http://localhost:8501', '_blank');
        });

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
        }

        // Drag and drop functionality
        dragDropZone.addEventListener('dragover', (極端e) => {
            e.preventDefault();
            dragDropZone.classList.add('drag-over');
        });

        dragDropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dragDropZone.classList.remove('drag-over');
        });

        dragDropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dragDropZone.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files).filter(file => 
                file.name.toLowerCase().endsWith('.csv')
            );
            
            if (files.length > 0) {
                uploadFiles(files);
            } else {
                showStatus('Please drop only CSV files.', 'error');
            }
        });

        // Prevent default drag behavior on the document
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
        });

        // Navigation between dashboard and CSV upload
        getStartedBtn.addEventListener('click', function() {
            document.getElementById('dashboard').classList.remove('active');
            document.getElementById('csvUploadContainer').classList.add('active');
        });

        backToDashboard.addEventListener('click', function() {
            document.getElementById('csvUploadContainer').classList.remove('active');
            document.getElementById('dashboard').classList.add('active');
            // Reset status message
            statusMessage.style.display = 'none';
            // Hide dashboard button
            openDashboardBtn.style.display = 'none';
        });

        // Open Streamlit dashboard
        openDashboardBtn.addEventListener('click', function() {
            window.open('http://localhost:8501', '_blank');
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
        return jsonify(success=False, error="Invalid file type. Only CSV allowed.")

# --------------------- Run App ---------------------

if __name__ == "__main__":
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Optional: Automatically open in browser
    webbrowser.open_new_tab("http://127.0.0.1:5000")
    app.run(debug=True, port=5000)