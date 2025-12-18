<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Voice Studio - Advanced Text to Speech</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3a0ca3;
            --accent-color: #4cc9f0;
            --light-color: #f8f9fa;
            --dark-color: #212529;
            --success-color: #4ade80;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .voice-control-slider {
            -webkit-appearance: none;
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: linear-gradient(to right, #4cc9f0, #4361ee);
            outline: none;
            margin: 10px 0;
        }
        
        .voice-control-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #4361ee;
            cursor: pointer;
            border: 3px solid white;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        }
        
        .preset-btn {
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        
        .preset-btn:hover {
            transform: translateY(-2px);
            border-color: var(--primary-color);
        }
        
        .preset-btn.active {
            background-color: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }
        
        .text-stats-card {
            background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
            border-left: 4px solid var(--primary-color);
        }
        
        .voice-card {
            transition: all 0.3s ease;
            cursor: pointer;
            border: 2px solid transparent;
        }
        
        .voice-card:hover {
            transform: translateY(-5px);
            border-color: var(--accent-color);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .voice-card.selected {
            border-color: var(--primary-color);
            background-color: rgba(67, 97, 238, 0.1);
        }
        
        .progress-ring {
            width: 80px;
            height: 80px;
        }
        
        .progress-ring-circle {
            transition: stroke-dashoffset 0.35s;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }
        
        .tab-content {
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .processing-step {
            opacity: 0.5;
            transition: all 0.3s ease;
        }
        
        .processing-step.active {
            opacity: 1;
            color: var(--primary-color);
            font-weight: bold;
        }
        
        .processing-step.completed {
            opacity: 1;
            color: var(--success-color);
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(67, 97, 238, 0); }
            100% { box-shadow: 0 0 0 0 rgba(67, 97, 238, 0); }
        }
        
        .result-card {
            animation: slideUp 0.5s ease;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .language-flag {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 8px;
        }
        
        .feature-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }
        
        .audio-wave {
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 3px;
        }
        
        .audio-bar {
            width: 4px;
            background: var(--primary-color);
            border-radius: 2px;
            animation: audioWave 1.5s ease-in-out infinite;
        }
        
        .audio-bar:nth-child(2) { animation-delay: 0.1s; }
        .audio-bar:nth-child(3) { animation-delay: 0.2s; }
        .audio-bar:nth-child(4) { animation-delay: 0.3s; }
        .audio-bar:nth-child(5) { animation-delay: 0.4s; }
        
        @keyframes audioWave {
            0%, 100% { height: 10px; }
            50% { height: 30px; }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-microphone-alt me-2"></i>
                <strong>AI Voice Studio</strong>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="#home">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#voices">Voices</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#api">API</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="container my-5" id="home">
        <div class="row">
            <!-- Left Sidebar - Controls -->
            <div class="col-lg-4 mb-4">
                <div class="glass-card p-4 mb-4">
                    <h4 class="mb-4"><i class="fas fa-sliders-h me-2"></i>Voice Controls</h4>
                    
                    <!-- Voice Selection -->
                    <div class="mb-4">
                        <label class="form-label"><i class="fas fa-user-voice me-2"></i>Select Voice</label>
                        <select class="form-select" id="voiceSelect">
                            <option value="">Loading voices...</option>
                        </select>
                        <div class="mt-2" id="voiceDetails"></div>
                    </div>
                    
                    <!-- Voice Parameters -->
                    <div class="mb-4">
                        <label class="form-label">Speed: <span id="rateValue">0%</span></label>
                        <input type="range" class="voice-control-slider" id="rateSlider" min="-100" max="100" value="0">
                        
                        <label class="form-label mt-3">Pitch: <span id="pitchValue">0Hz</span></label>
                        <input type="range" class="voice-control-slider" id="pitchSlider" min="-100" max="100" value="0">
                        
                        <label class="form-label mt-3">Volume: <span id="volumeValue">0%</span></label>
                        <input type="range" class="voice-control-slider" id="volumeSlider" min="-50" max="50" value="0">
                    </div>
                    
                    <!-- Presets -->
                    <div class="mb-4">
                        <label class="form-label"><i class="fas fa-bolt me-2"></i>Voice Presets</label>
                        <div class="d-flex flex-wrap gap-2">
                            <button class="btn btn-outline-primary preset-btn" onclick="applyPreset('slow')">
                                <i class="fas fa-turtle me-1"></i> Slow
                            </button>
                            <button class="btn btn-outline-primary preset-btn active" onclick="applyPreset('normal')">
                                <i class="fas fa-user me-1"></i> Normal
                            </button>
                            <button class="btn btn-outline-primary preset-btn" onclick="applyPreset('fast')">
                                <i class="fas fa-running me-1"></i> Fast
                            </button>
                            <button class="btn btn-outline-primary preset-btn" onclick="applyPreset('highPitch')">
                                <i class="fas fa-arrow-up me-1"></i> High Pitch
                            </button>
                            <button class="btn btn-outline-primary preset-btn" onclick="applyPreset('lowPitch')">
                                <i class="fas fa-arrow-down me-1"></i> Low Pitch
                            </button>
                        </div>
                    </div>
                    
                    <!-- Processing Options -->
                    <div class="mb-4">
                        <label class="form-label"><i class="fas fa-cog me-2"></i>Text Processing</label>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="autoCapitalize" checked>
                            <label class="form-check-label" for="autoCapitalize">
                                Auto Capitalize Sentences
                            </label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="cleanSpaces" checked>
                            <label class="form-check-label" for="cleanSpaces">
                                Clean Extra Spaces
                            </label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="correctGrammar">
                            <label class="form-check-label" for="correctGrammar">
                                Auto Grammar Correction
                            </label>
                        </div>
                    </div>
                    
                    <!-- Translation -->
                    <div class="mb-4">
                        <label class="form-label"><i class="fas fa-language me-2"></i>Translation</label>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="enableTranslation">
                            <label class="form-check-label" for="enableTranslation">
                                Enable Translation
                            </label>
                        </div>
                        <div id="translationOptions" style="display: none;">
                            <select class="form-select mb-2" id="targetLanguage">
                                <option value="en">English</option>
                                <option value="es">Spanish</option>
                                <option value="fr">French</option>
                                <option value="de">German</option>
                                <option value="hi">Hindi</option>
                                <option value="ja">Japanese</option>
                                <option value="zh-cn">Chinese</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Text Statistics -->
                <div class="glass-card p-4">
                    <h5><i class="fas fa-chart-bar me-2"></i>Text Statistics</h5>
                    <div class="text-stats-card p-3 mb-3">
                        <div class="row text-center">
                            <div class="col-4">
                                <h3 id="wordCount">0</h3>
                                <small class="text-muted">Words</small>
                            </div>
                            <div class="col-4">
                                <h3 id="charCount">0</h3>
                                <small class="text-muted">Characters</small>
                            </div>
                            <div class="col-4">
                                <h3 id="sentenceCount">0</h3>
                                <small class="text-muted">Sentences</small>
                            </div>
                        </div>
                    </div>
                    <div class="text-center">
                        <div class="progress-ring d-inline-block">
                            <svg viewBox="0 0 36 36">
                                <path d="M18 2.0845
                                    a 15.9155 15.9155 0 0 1 0 31.831
                                    a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none"
                                    stroke="#e0e0e0"
                                    stroke-width="3"/>
                                <path class="progress-ring-circle"
                                    d="M18 2.0845
                                    a 15.9155 15.9155 0 0 1 0 31.831
                                    a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none"
                                    stroke="#4361ee"
                                    stroke-width="3"
                                    stroke-dasharray="100, 100"/>
                                <text x="18" y="20.35" text-anchor="middle" fill="#4361ee" font-size="8">0%</text>
                            </svg>
                        </div>
                        <p class="mt-2" id="readingTime">Reading time: 0 min</p>
                    </div>
                </div>
            </div>
            
            <!-- Main Content Area -->
            <div class="col-lg-8">
                <div class="glass-card p-4 mb-4">
                    <!-- Text Input Area -->
                    <div class="mb-4">
                        <label class="form-label"><i class="fas fa-edit me-2"></i>Enter Text</label>
                        <textarea class="form-control" id="textInput" rows="8" 
                                  placeholder="Enter your text here... You can paste text from any source. The system will process it automatically."></textarea>
                    </div>
                    
                    <!-- Text Processing Controls -->
                    <div class="mb-4">
                        <label class="form-label"><i class="fas fa-magic me-2"></i>Text Tools</label>
                        <div class="d-flex flex-wrap gap-2 mb-3">
                            <button class="btn btn-outline-secondary" onclick="processText('lowercase')">
                                <i class="fas fa-font"></i> Lowercase
                            </button>
                            <button class="btn btn-outline-secondary" onclick="processText('uppercase')">
                                <i class="fas fa-text-height"></i> Uppercase
                            </button>
                            <button class="btn btn-outline-secondary" onclick="processText('titleCase')">
                                <i class="fas fa-heading"></i> Title Case
                            </button>
                            <button class="btn btn-outline-secondary" onclick="processText('reverse')">
                                <i class="fas fa-exchange-alt"></i> Reverse
                            </button>
                            <button class="btn btn-outline-secondary" onclick="processText('sortAlpha')">
                                <i class="fas fa-sort-alpha-down"></i> Sort A-Z
                            </button>
                            <button class="btn btn-outline-secondary" onclick="processText('removeSpecial')">
                                <i class="fas fa-ban"></i> Remove Special
                            </button>
                            <button class="btn btn-outline-secondary" onclick="analyzeText()">
                                <i class="fas fa-chart-line"></i> Analyze
                            </button>
                            <button class="btn btn-outline-secondary" onclick="checkGrammar()">
                                <i class="fas fa-spell-check"></i> Check Grammar
                            </button>
                        </div>
                        
                        <!-- Sort Options -->
                        <div class="input-group mb-3">
                            <span class="input-group-text"><i class="fas fa-sort"></i></span>
                            <select class="form-select" id="sortOption">
                                <option value="none">No Sorting</option>
                                <option value="alphabetical">Sort Alphabetically</option>
                                <option value="reverse">Reverse Order</option>
                                <option value="length">Sort by Length</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Processing Steps -->
                    <div class="mb-4">
                        <div class="processing-steps d-flex justify-content-between mb-3">
                            <div class="processing-step text-center active" id="step1">
                                <div class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-2" 
                                     style="width: 40px; height: 40px;">1</div>
                                <div>Input</div>
                            </div>
                            <div class="processing-step text-center" id="step2">
                                <div class="rounded-circle bg-secondary text-white d-inline-flex align-items-center justify-content-center mb-2" 
                                     style="width: 40px; height: 40px;">2</div>
                                <div>Processing</div>
                            </div>
                            <div class="processing-step text-center" id="step3">
                                <div class="rounded-circle bg-secondary text-white d-inline-flex align-items-center justify-content-center mb-2" 
                                     style="width: 40px; height: 40px;">3</div>
                                <div>Generating</div>
                            </div>
                            <div class="processing-step text-center" id="step4">
                                <div class="rounded-circle bg-secondary text-white d-inline-flex align-items-center justify-content-center mb-2" 
                                     style="width: 40px; height: 40px;">4</div>
                                <div>Complete</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Generate Button -->
                    <div class="text-center">
                        <button class="btn btn-primary btn-lg px-5 py-3 pulse-animation" onclick="generateVoice()" id="generateBtn">
                            <i class="fas fa-play-circle me-2"></i> Generate Voice
                        </button>
                    </div>
                </div>
                
                <!-- Results Section -->
                <div class="glass-card p-4 mb-4" id="resultsSection" style="display: none;">
                    <h4 class="mb-3"><i class="fas fa-music me-2"></i>Generated Audio</h4>
                    <div class="result-card p-3 mb-3">
                        <div class="audio-wave mb-3" id="audioWave">
                            <div class="audio-bar"></div>
                            <div class="audio-bar"></div>
                            <div class="audio-bar"></div>
                            <div class="audio-bar"></div>
                            <div class="audio-bar"></div>
                        </div>
                        <audio controls class="w-100 mb-3" id="audioPlayer"></audio>
                        <div class="d-flex justify-content-between">
                            <button class="btn btn-outline-primary" onclick="downloadAudio()">
                                <i class="fas fa-download me-2"></i> Download
                            </button>
                            <button class="btn btn-outline-success" onclick="shareAudio()">
                                <i class="fas fa-share-alt me-2"></i> Share
                            </button>
                            <button class="btn btn-outline-danger" onclick="stopAudio()">
                                <i class="fas fa-stop me-2"></i> Stop
                            </button>
                        </div>
                    </div>
                    <div class="mt-3" id="processingDetails"></div>
                </div>
                
                <!-- Features Section -->
                <div class="glass-card p-4" id="features">
                    <h4 class="mb-4"><i class="fas fa-star me-2"></i>Advanced Features</h4>
                    <div class="row">
                        <div class="col-md-3 mb-3 text-center">
                            <div class="feature-icon">
                                <i class="fas fa-language fa-2x"></i>
                            </div>
                            <h6>Multi-language</h6>
                            <small class="text-muted">Support for 20+ languages</small>
                        </div>
                        <div class="col-md-3 mb-3 text-center">
                            <div class="feature-icon">
                                <i class="fas fa-spell-check fa-2x"></i>
                            </div>
                            <h6>Grammar Check</h6>
                            <small class="text-muted">AI-powered grammar correction</small>
                        </div>
                        <div class="col-md-3 mb-3 text-center">
                            <div class="feature-icon">
                                <i class="fas fa-exchange-alt fa-2x"></i>
                            </div>
                            <h6>Translation</h6>
                            <small class="text-muted">Real-time text translation</small>
                        </div>
                        <div class="col-md-3 mb-3 text-center">
                            <div class="feature-icon">
                                <i class="fas fa-sliders-h fa-2x"></i>
                            </div>
                            <h6>Fine Control</h6>
                            <small class="text-muted">Precise voice parameter tuning</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Voices Gallery Section -->
    <div class="container my-5" id="voices">
        <div class="glass-card p-4">
            <h4 class="mb-4"><i class="fas fa-user-voice me-2"></i>Voice Gallery</h4>
            <div class="row" id="voicesGallery">
                <!-- Voices will be loaded here -->
            </div>
        </div>
    </div>

    <!-- Modals -->
    <!-- Grammar Check Modal -->
    <div class="modal fade" id="grammarModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-spell-check me-2"></i>Grammar Check Results</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="grammarResults">
                    <!-- Grammar results will appear here -->
                </div>
            </div>
        </div>
    </div>
    
    <!-- Text Analysis Modal -->
    <div class="modal fade" id="analysisModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-chart-line me-2"></i>Text Analysis</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="analysisResults">
                    <!-- Analysis results will appear here -->
                </div>
            </div>
        </div>
    </div>

    <!-- Loading Spinner -->
    <div class="modal fade" id="loadingModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content glass-card">
                <div class="modal-body text-center py-5">
                    <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <h5 id="loadingMessage">Processing your request...</h5>
                    <div class="mt-3" id="loadingProgress"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="text-center text-white py-4 mt-5">
        <div class="container">
            <p class="mb-2">AI Voice Studio &copy; 2024 - Advanced Text to Speech System</p>
            <p class="small mb-0">
                <i class="fas fa-server me-1"></i> Powered by Edge TTS & AI Processing
                <span class="mx-2">•</span>
                <i class="fas fa-code me-1"></i> Built with Flask & Bootstrap
            </p>
        </div>
    </footer>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script>
        // Global variables
        let voices = [];
        let currentAudio = null;
        let audioUrl = null;
        let processingSteps = ['step1', 'step2', 'step3', 'step4'];
        
        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {
            loadVoices();
            setupEventListeners();
            updateTextStatistics();
            
            // Update backend URL based on environment
            window.API_BASE_URL = window.location.hostname === 'localhost' 
                ? 'http://localhost:5000/api' 
                : '/api';
        });
        
        // Setup event listeners
        function setupEventListeners() {
            const textInput = document.getElementById('textInput');
            const rateSlider = document.getElementById('rateSlider');
            const pitchSlider = document.getElementById('pitchSlider');
            const volumeSlider = document.getElementById('volumeSlider');
            const enableTranslation = document.getElementById('enableTranslation');
            
            // Text input events
            textInput.addEventListener('input', updateTextStatistics);
            textInput.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    generateVoice();
                }
            });
            
            // Slider events
            rateSlider.addEventListener('input', function() {
                document.getElementById('rateValue').textContent = this.value + '%';
            });
            
            pitchSlider.addEventListener('input', function() {
                document.getElementById('pitchValue').textContent = this.value + 'Hz';
            });
            
            volumeSlider.addEventListener('input', function() {
                document.getElementById('volumeValue').textContent = this.value + '%';
            });
            
            // Translation toggle
            enableTranslation.addEventListener('change', function() {
                document.getElementById('translationOptions').style.display = 
                    this.checked ? 'block' : 'none';
            });
            
            // Audio player events
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.addEventListener('play', function() {
                document.getElementById('audioWave').style.display = 'flex';
            });
            audioPlayer.addEventListener('pause', function() {
                document.getElementById('audioWave').style.display = 'none';
            });
        }
        
        // Load available voices
        async function loadVoices() {
            try {
                showLoading('Loading voices...');
                const response = await fetch(`${window.API_BASE_URL}/voices`);
                const data = await response.json();
                
                if (data.voices) {
                    voices = data.voices;
                    populateVoiceSelect(data.voices);
                    populateVoiceGallery(data.voices);
                }
                hideLoading();
            } catch (error) {
                console.error('Error loading voices:', error);
                hideLoading();
                showAlert('Error', 'Failed to load voices. Please refresh the page.', 'error');
            }
        }
        
        // Populate voice select dropdown
        function populateVoiceSelect(voiceCatalog) {
            const voiceSelect = document.getElementById('voiceSelect');
            voiceSelect.innerHTML = '<option value="">Select a voice...</option>';
            
            for (const [category, voices] of Object.entries(voiceCatalog)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = category.charAt(0).toUpperCase() + category.slice(1) + ' Voices';
                
                for (const [id, voiceInfo] of Object.entries(voices)) {
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = `${voiceInfo.name} (${voiceInfo.language})`;
                    optgroup.appendChild(option);
                }
                
                voiceSelect.appendChild(optgroup);
            }
            
            voiceSelect.addEventListener('change', function() {
                const selectedVoice = this.value;
                updateVoiceDetails(selectedVoice);
            });
            
            // Select default voice
            voiceSelect.value = 'en-US-JennyNeural';
            updateVoiceDetails('en-US-JennyNeural');
        }
        
        // Populate voice gallery
        function populateVoiceGallery(voiceCatalog) {
            const gallery = document.getElementById('voicesGallery');
            gallery.innerHTML = '';
            
            for (const [category, voices] of Object.entries(voiceCatalog)) {
                for (const [id, voiceInfo] of Object.entries(voices)) {
                    const col = document.createElement('div');
                    col.className = 'col-md-3 mb-3';
                    
                    const genderIcon = voiceInfo.gender === 'Female' ? 'fa-female' : 'fa-male';
                    const isSelected = id === 'en-US-JennyNeural' ? 'selected' : '';
                    
                    col.innerHTML = `
                        <div class="voice-card p-3 ${isSelected}" onclick="selectVoice('${id}')">
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas ${genderIcon} me-2 ${voiceInfo.gender === 'Female' ? 'text-pink' : 'text-blue'}"></i>
                                <strong>${voiceInfo.name}</strong>
                            </div>
                            <div class="small text-muted mb-2">
                                <i class="fas fa-globe me-1"></i> ${voiceInfo.language}
                            </div>
                            <div class="text-primary small">
                                <i class="fas fa-id-card me-1"></i> ${id}
                            </div>
                        </div>
                    `;
                    
                    gallery.appendChild(col);
                }
            }
        }
        
        // Update voice details display
        function updateVoiceDetails(voiceId) {
            const detailsDiv = document.getElementById('voiceDetails');
            
            // Find voice in catalog
            for (const category in voices) {
                if (voices[category][voiceId]) {
                    const voice = voices[category][voiceId];
                    detailsDiv.innerHTML = `
                        <div class="alert alert-info py-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${voice.name}</strong><br>
                                    <small class="text-muted">
                                        <i class="fas fa-globe"></i> ${voice.language} | 
                                        <i class="fas ${voice.gender === 'Female' ? 'fa-female' : 'fa-male'}"></i> ${voice.gender}
                                    </small>
                                </div>
                                <div>
                                    <button class="btn btn-sm btn-outline-primary" onclick="previewVoice('${voiceId}')">
                                        <i class="fas fa-play"></i> Preview
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    return;
                }
            }
            
            detailsDiv.innerHTML = '<div class="alert alert-warning">Select a voice to see details</div>';
        }
        
        // Select voice from gallery
        function selectVoice(voiceId) {
            document.getElementById('voiceSelect').value = voiceId;
            updateVoiceDetails(voiceId);
            
            // Update gallery selection
            document.querySelectorAll('.voice-card').forEach(card => {
                card.classList.remove('selected');
            });
            event.currentTarget.classList.add('selected');
        }
        
        // Preview voice with sample text
        async function previewVoice(voiceId) {
            const sampleText = "Hello, this is a preview of how I sound.";
            const rate = document.getElementById('rateSlider').value;
            const pitch = document.getElementById('pitchSlider').value;
            
            await generateVoice(sampleText, voiceId, rate, pitch, true);
        }
        
        // Apply voice preset
        function applyPreset(preset) {
            const rateSlider = document.getElementById('rateSlider');
            const pitchSlider = document.getElementById('pitchSlider');
            
            // Reset all preset buttons
            document.querySelectorAll('.preset-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Mark clicked button as active
            event.currentTarget.classList.add('active');
            
            switch(preset) {
                case 'slow':
                    rateSlider.value = -50;
                    pitchSlider.value = 0;
                    break;
                case 'normal':
                    rateSlider.value = 0;
                    pitchSlider.value = 0;
                    break;
                case 'fast':
                    rateSlider.value = 50;
                    pitchSlider.value = 0;
                    break;
                case 'highPitch':
                    rateSlider.value = 0;
                    pitchSlider.value = 50;
                    break;
                case 'lowPitch':
                    rateSlider.value = 0;
                    pitchSlider.value = -50;
                    break;
            }
            
            // Update displays
            rateSlider.dispatchEvent(new Event('input'));
            pitchSlider.dispatchEvent(new Event('input'));
        }
        
        // Process text with specific operation
        function processText(operation) {
            const textInput = document.getElementById('textInput');
            let text = textInput.value;
            
            switch(operation) {
                case 'lowercase':
                    text = text.toLowerCase();
                    break;
                case 'uppercase':
                    text = text.toUpperCase();
                    break;
                case 'titleCase':
                    text = text.toLowerCase().split(' ').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ');
                    break;
                case 'reverse':
                    text = text.split('').reverse().join('');
                    break;
                case 'sortAlpha':
                    text = text.split('\n').sort().join('\n');
                    break;
                case 'removeSpecial':
                    text = text.replace(/[^\w\s.,!?]/g, '');
                    break;
            }
            
            textInput.value = text;
            updateTextStatistics();
            showAlert('Success', 'Text processed successfully!', 'success');
        }
        
        // Update text statistics
        function updateTextStatistics() {
            const text = document.getElementById('textInput').value;
            const words = text.trim() ? text.trim().split(/\s+/) : [];
            const sentences = text.trim() ? text.split(/[.!?]+/).filter(s => s.trim()) : [];
            
            document.getElementById('wordCount').textContent = words.length;
            document.getElementById('charCount').textContent = text.length;
            document.getElementById('sentenceCount').textContent = sentences.length;
            
            // Calculate reading time
            const readingTimeMinutes = words.length / 200;
            document.getElementById('readingTime').textContent = 
                `Reading time: ${readingTimeMinutes.toFixed(1)} min`;
            
            // Update progress ring (complexity)
            const complexity = Math.min(100, (words.length / 500) * 100);
            const circle = document.querySelector('.progress-ring-circle');
            const radius = 15.9155;
            const circumference = 2 * Math.PI * radius;
            const offset = circumference - (complexity / 100) * circumference;
            
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = offset;
            
            // Update percentage text
            document.querySelector('.progress-ring text').textContent = Math.round(complexity) + '%';
        }
        
        // Check grammar
        async function checkGrammar() {
            const text = document.getElementById('textInput').value.trim();
            if (!text) {
                showAlert('Warning', 'Please enter some text first.', 'warning');
                return;
            }
            
            try {
                showLoading('Checking grammar...');
                
                const response = await fetch(`${window.API_BASE_URL}/grammar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    throw new Error(result.error);
                }
                
                displayGrammarResults(result);
                hideLoading();
                
            } catch (error) {
                console.error('Grammar check error:', error);
                hideLoading();
                showAlert('Error', 'Failed to check grammar. Please try again.', 'error');
            }
        }
        
        // Display grammar results
        function displayGrammarResults(result) {
            const modalBody = document.getElementById('grammarResults');
            
            if (result.errors_found === 0) {
                modalBody.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle me-2"></i>
                        No grammar errors found! Your text is well-written.
                    </div>
                    <div class="mt-3">
                        <h6>Original Text:</h6>
                        <p class="text-muted">${result.original}</p>
                    </div>
                `;
            } else {
                let correctionsHTML = '<div class="alert alert-warning">';
                correctionsHTML += `<i class="fas fa-exclamation-triangle me-2"></i>`;
                correctionsHTML += `Found ${result.errors_found} grammar issue(s)</div>`;
                
                correctionsHTML += '<div class="mt-3"><h6>Corrections Applied:</h6>';
                correctionsHTML += `<p><strong>Before:</strong> ${result.original}</p>`;
                correctionsHTML += `<p><strong>After:</strong> ${result.corrected}</p></div>`;
                
                if (result.corrections.length > 0) {
                    correctionsHTML += '<div class="mt-3"><h6>Issues Found:</h6><ul class="list-group">';
                    result.corrections.forEach(correction => {
                        correctionsHTML += `
                            <li class="list-group-item">
                                <small>${correction.message}</small><br>
                                <span class="text-muted">Suggestions: ${correction.replacements?.join(', ') || 'None'}</span>
                            </li>
                        `;
                    });
                    correctionsHTML += '</ul></div>';
                }
                
                correctionsHTML += `
                    <div class="mt-3">
                        <button class="btn btn-primary" onclick="applyGrammarCorrection('${result.corrected.replace(/'/g, "\\'")}')">
                            <i class="fas fa-check me-2"></i> Apply Corrections
                        </button>
                    </div>
                `;
                
                modalBody.innerHTML = correctionsHTML;
            }
            
            // Show modal
            const grammarModal = new bootstrap.Modal(document.getElementById('grammarModal'));
            grammarModal.show();
        }
        
        // Apply grammar correction to text area
        function applyGrammarCorrection(correctedText) {
            document.getElementById('textInput').value = correctedText;
            updateTextStatistics();
            bootstrap.Modal.getInstance(document.getElementById('grammarModal')).hide();
            showAlert('Success', 'Grammar corrections applied!', 'success');
        }
        
        // Analyze text
        async function analyzeText() {
            const text = document.getElementById('textInput').value.trim();
            if (!text) {
                showAlert('Warning', 'Please enter some text first.', 'warning');
                return;
            }
            
            try {
                showLoading('Analyzing text...');
                
                const response = await fetch(`${window.API_BASE_URL}/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    throw new Error(result.error);
                }
                
                displayAnalysisResults(result);
                hideLoading();
                
            } catch (error) {
                console.error('Text analysis error:', error);
                hideLoading();
                showAlert('Error', 'Failed to analyze text. Please try again.', 'error');
            }
        }
        
        // Display analysis results
        function displayAnalysisResults(result) {
            const modalBody = document.getElementById('analysisResults');
            const metrics = result.metrics;
            const suggestions = result.suggestions;
            
            let html = `
                <div class="row">
                    <div class="col-6 mb-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="card-title">${metrics.word_count}</h3>
                                <p class="card-text text-muted">Words</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="card-title">${metrics.sentence_count}</h3>
                                <p class="card-text text-muted">Sentences</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <h6>Detailed Metrics:</h6>
                    <table class="table table-sm">
                        <tr>
                            <td>Average Word Length:</td>
                            <td class="text-end">${metrics.average_word_length} characters</td>
                        </tr>
                        <tr>
                            <td>Average Sentence Length:</td>
                            <td class="text-end">${metrics.average_sentence_length} words</td>
                        </tr>
                        <tr>
                            <td>Estimated Reading Time:</td>
                            <td class="text-end">${metrics.estimated_reading_time_minutes} minutes</td>
                        </tr>
                        <tr>
                            <td>Complexity Score:</td>
                            <td class="text-end">${metrics.complexity_score}/100</td>
                        </tr>
                    </table>
                </div>
            `;
            
            if (suggestions && suggestions.length > 0) {
                html += `
                    <div class="alert alert-info">
                        <h6><i class="fas fa-lightbulb me-2"></i>Suggestions:</h6>
                        <ul class="mb-0">
                            ${suggestions.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            
            modalBody.innerHTML = html;
            
            // Show modal
            const analysisModal = new bootstrap.Modal(document.getElementById('analysisModal'));
            analysisModal.show();
        }
        
        // Generate voice
        async function generateVoice(previewText = null, previewVoice = null, previewRate = null, previewPitch = null, isPreview = false) {
            let text = previewText || document.getElementById('textInput').value.trim();
            const voice = previewVoice || document.getElementById('voiceSelect').value;
            const rate = previewRate || document.getElementById('rateSlider').value;
            const pitch = previewPitch || document.getElementById('pitchSlider').value;
            const volume = document.getElementById('volumeSlider').value;
            
            if (!text && !isPreview) {
                showAlert('Warning', 'Please enter some text first.', 'warning');
                return;
            }
            
            if (!voice) {
                showAlert('Warning', 'Please select a voice.', 'warning');
                return;
            }
            
            // If preview with no text, use default
            if (isPreview && !text) {
                text = "This is a voice preview.";
            }
            
            try {
                // Show processing steps
                updateProcessingStep(1);
                
                // Prepare request data
                const requestData = {
                    text: text,
                    voice: voice,
                    rate: parseInt(rate),
                    pitch: parseInt(pitch),
                    volume: parseInt(volume),
                    preprocess: document.getElementById('autoCapitalize').checked || 
                               document.getElementById('cleanSpaces').checked ||
                               document.getElementById('sortOption').value !== 'none',
                    processing_options: {
                        lowercase: false,
                        uppercase: false,
                        clean_spaces: document.getElementById('cleanSpaces').checked,
                        capitalize_sentences: document.getElementById('autoCapitalize').checked,
                        sort_option: document.getElementById('sortOption').value
                    },
                    correct_grammar: document.getElementById('correctGrammar').checked,
                    translate: document.getElementById('enableTranslation').checked,
                    target_language: document.getElementById('targetLanguage').value
                };
                
                if (!isPreview) {
                    showLoading('Processing your request...');
                    updateProcessingStep(2);
                }
                
                // Send request
                const response = await fetch(`${window.API_BASE_URL}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Generation failed');
                }
                
                if (!isPreview) {
                    updateProcessingStep(3);
                }
                
                // Get audio blob
                const blob = await response.blob();
                audioUrl = URL.createObjectURL(blob);
                
                if (!isPreview) {
                    updateProcessingStep(4);
                    hideLoading();
                    showResults(audioUrl);
                } else {
                    // For preview, play directly
                    const audio = new Audio(audioUrl);
                    audio.play();
                    currentAudio = audio;
                }
                
            } catch (error) {
                console.error('Voice generation error:', error);
                hideLoading();
                resetProcessingSteps();
                
                if (!isPreview) {
                    showAlert('Error', error.message || 'Failed to generate voice. Please try again.', 'error');
                }
            }
        }
        
        // Update processing step
        function updateProcessingStep(stepNumber) {
            // Reset all steps
            processingSteps.forEach(step => {
                const stepElement = document.getElementById(step);
                stepElement.classList.remove('active', 'completed');
                stepElement.querySelector('div:first-child').classList.remove('bg-primary', 'bg-success');
                stepElement.querySelector('div:first-child').classList.add('bg-secondary');
            });
            
            // Mark completed steps
            for (let i = 1; i < stepNumber; i++) {
                const stepElement = document.getElementById(`step${i}`);
                stepElement.classList.add('completed');
                stepElement.querySelector('div:first-child').classList.remove('bg-secondary');
                stepElement.querySelector('div:first-child').classList.add('bg-success');
            }
            
            // Mark current step
            const currentStep = document.getElementById(`step${stepNumber}`);
            if (currentStep) {
                currentStep.classList.add('active');
                currentStep.querySelector('div:first-child').classList.remove('bg-secondary');
                currentStep.querySelector('div:first-child').classList.add('bg-primary');
            }
        }
        
        // Reset processing steps
        function resetProcessingSteps() {
            processingSteps.forEach(step => {
                const stepElement = document.getElementById(step);
                stepElement.classList.remove('active', 'completed');
                stepElement.querySelector('div:first-child').classList.remove('bg-primary', 'bg-success');
                stepElement.querySelector('div:first-child').classList.add('bg-secondary');
            });
            
            // Set first step as active
            document.getElementById('step1').classList.add('active');
            document.getElementById('step1').querySelector('div:first-child').classList.remove('bg-secondary');
            document.getElementById('step1').querySelector('div:first-child').classList.add('bg-primary');
        }
        
        // Show results section
        function showResults(audioUrl) {
            const resultsSection = document.getElementById('resultsSection');
            const audioPlayer = document.getElementById('audioPlayer');
            
            audioPlayer.src = audioUrl;
            resultsSection.style.display = 'block';
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            
            // Show processing details
            const detailsDiv = document.getElementById('processingDetails');
            const voiceName = document.getElementById('voiceSelect').options[document.getElementById('voiceSelect').selectedIndex].text;
            
            detailsDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-check-circle me-2"></i>Voice Generated Successfully!</h6>
                    <small>
                        Voice: ${voiceName}<br>
                        Speed: ${document.getElementById('rateSlider').value}% | 
                        Pitch: ${document.getElementById('pitchSlider').value}Hz<br>
                        Generated at: ${new Date().toLocaleTimeString()}
                    </small>
                </div>
            `;
        }
        
        // Download audio
        function downloadAudio() {
            if (!audioUrl) return;
            
            const a = document.createElement('a');
            a.href = audioUrl;
            a.download = `voice_${Date.now()}.mp3`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            showAlert('Success', 'Audio download started!', 'success');
        }
        
        // Share audio
        function shareAudio() {
            if (navigator.share) {
                navigator.share({
                    title: 'AI Generated Voice',
                    text: 'Check out this AI-generated voice from AI Voice Studio!',
                    url: audioUrl
                });
            } else {
                // Fallback: Copy URL to clipboard
                navigator.clipboard.writeText(audioUrl).then(() => {
                    showAlert('Success', 'Audio link copied to clipboard!', 'success');
                });
            }
        }
        
        // Stop audio
        function stopAudio() {
            if (currentAudio) {
                currentAudio.pause();
                currentAudio.currentTime = 0;
            }
            
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            document.getElementById('audioWave').style.display = 'none';
        }
        
        // Show loading modal
        function showLoading(message) {
            document.getElementById('loadingMessage').textContent = message;
            const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
            loadingModal.show();
        }
        
        // Hide loading modal
        function hideLoading() {
            const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
            if (loadingModal) {
                loadingModal.hide();
            }
        }
        
        // Show alert
        function showAlert(title, text, icon) {
            Swal.fire({
                title: title,
                text: text,
                icon: icon,
                confirmButtonColor: '#4361ee',
                timer: 3000,
                timerProgressBar: true
            });
        }
    </script>
</body>
</html>
