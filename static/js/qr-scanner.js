// QR Scanner functionality for TrustHarvest

class TrustHarvestQRScanner {
    constructor() {
        this.scanner = null;
        this.isScanning = false;
        this.cameras = [];
        this.currentCameraIndex = 0;
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        this.elements = {
            reader: document.getElementById('qr-reader'),
            startButton: document.getElementById('start-scanner'),
            stopButton: document.getElementById('stop-scanner'),
            statusDiv: document.getElementById('scanner-status'),
            manualForm: document.getElementById('manual-form'),
            batchIdInput: document.getElementById('batch-id'),
            switchCameraButton: document.getElementById('switch-camera'),
            torchButton: document.getElementById('torch-button')
        };
    }
    
    bindEvents() {
        if (this.elements.startButton) {
            this.elements.startButton.addEventListener('click', () => this.startScanner());
        }
        
        if (this.elements.stopButton) {
            this.elements.stopButton.addEventListener('click', () => this.stopScanner());
        }
        
        if (this.elements.manualForm) {
            this.elements.manualForm.addEventListener('submit', (e) => this.handleManualSubmit(e));
        }
        
        if (this.elements.switchCameraButton) {
            this.elements.switchCameraButton.addEventListener('click', () => this.switchCamera());
        }
        
        if (this.elements.torchButton) {
            this.elements.torchButton.addEventListener('click', () => this.toggleTorch());
        }
        
        // Bind sample batch ID buttons
        document.querySelectorAll('.try-sample').forEach(button => {
            button.addEventListener('click', (e) => this.handleSampleClick(e));
        });
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isScanning) {
                this.stopScanner();
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (this.isScanning) {
                this.restartScanner();
            }
        });
    }
    
    async getCameras() {
        try {
            const devices = await Html5Qrcode.getCameras();
            this.cameras = devices;
            return devices;
        } catch (error) {
            console.error('Error getting cameras:', error);
            this.updateStatus('danger', 'Unable to access cameras. Please check permissions.');
            return [];
        }
    }
    
    async startScanner() {
        if (this.isScanning) return;
        
        try {
            this.updateStatus('info', 'Initializing camera...');
            this.setButtonStates(true);
            
            const cameras = await this.getCameras();
            
            if (cameras.length === 0) {
                throw new Error('No cameras found');
            }
            
            // Update camera switch button visibility
            if (this.elements.switchCameraButton) {
                this.elements.switchCameraButton.style.display = cameras.length > 1 ? 'inline-block' : 'none';
            }
            
            this.scanner = new Html5Qrcode(this.elements.reader.id);
            
            const cameraId = cameras[this.currentCameraIndex]?.id || cameras[0].id;
            
            const config = {
                fps: 10,
                qrbox: { 
                    width: Math.min(300, window.innerWidth * 0.8), 
                    height: Math.min(300, window.innerWidth * 0.8) 
                },
                aspectRatio: 1.0,
                disableFlip: false
            };
            
            await this.scanner.start(
                cameraId,
                config,
                (decodedText, decodedResult) => this.onScanSuccess(decodedText, decodedResult),
                (errorMessage) => this.onScanFailure(errorMessage)
            );
            
            this.isScanning = true;
            this.updateStatus('success', 'Scanner active. Point your camera at a QR code.');
            
            // Check for torch support
            this.checkTorchSupport();
            
        } catch (error) {
            console.error('Error starting scanner:', error);
            this.handleScannerError(error);
            this.setButtonStates(false);
        }
    }
    
    async stopScanner() {
        if (!this.scanner || !this.isScanning) return;
        
        try {
            await this.scanner.stop();
            this.scanner.clear();
            this.scanner = null;
            this.isScanning = false;
            this.setButtonStates(false);
            this.updateStatus('secondary', 'Scanner stopped.');
        } catch (error) {
            console.error('Error stopping scanner:', error);
            this.updateStatus('warning', 'Error stopping scanner.');
        }
    }
    
    async restartScanner() {
        if (this.isScanning) {
            await this.stopScanner();
            setTimeout(() => this.startScanner(), 500);
        }
    }
    
    async switchCamera() {
        if (!this.isScanning || this.cameras.length <= 1) return;
        
        this.currentCameraIndex = (this.currentCameraIndex + 1) % this.cameras.length;
        await this.restartScanner();
    }
    
    async toggleTorch() {
        if (!this.scanner || !this.isScanning) return;
        
        try {
            const stream = this.scanner.getRunningTrackCapabilities();
            if (stream && stream.torch) {
                const track = this.scanner.getRunningTrackSettings();
                await this.scanner.applyVideoConstraints({
                    torch: !track.torch
                });
                
                // Update torch button appearance
                if (this.elements.torchButton) {
                    this.elements.torchButton.classList.toggle('active');
                }
            }
        } catch (error) {
            console.error('Error toggling torch:', error);
        }
    }
    
    checkTorchSupport() {
        if (!this.scanner || !this.elements.torchButton) return;
        
        try {
            const capabilities = this.scanner.getRunningTrackCapabilities();
            if (capabilities && capabilities.torch) {
                this.elements.torchButton.style.display = 'inline-block';
            } else {
                this.elements.torchButton.style.display = 'none';
            }
        } catch (error) {
            this.elements.torchButton.style.display = 'none';
        }
    }
    
    onScanSuccess(decodedText, decodedResult) {
        console.log('QR Code scanned:', decodedText);
        
        // Extract batch ID from the scanned text
        let batchId = this.extractBatchId(decodedText);
        
        if (batchId) {
            this.updateStatus('success', `QR Code detected! Batch ID: ${batchId}`);
            this.stopScanner();
            
            // Add visual feedback
            this.showScanSuccess();
            
            // Redirect after a short delay
            setTimeout(() => {
                window.location.href = `/scan/${batchId}`;
            }, 1500);
        } else {
            this.updateStatus('warning', 'QR code detected but no valid batch ID found.');
        }
    }
    
    onScanFailure(errorMessage) {
        // Silently handle scan failures to avoid spam
        // Only log to console for debugging
        // console.warn('Scan failure:', errorMessage);
    }
    
    extractBatchId(scannedText) {
        // Handle different QR code formats
        if (scannedText.includes('/scan/')) {
            // URL format: http://domain.com/scan/BATCH_ID
            return scannedText.split('/scan/')[1];
        } else if (scannedText.startsWith('TH')) {
            // Direct batch ID format: TH20240115ABCD1234
            return scannedText;
        } else if (scannedText.includes('batch=')) {
            // Query parameter format: ?batch=TH20240115ABCD1234
            const urlParams = new URLSearchParams(scannedText.split('?')[1]);
            return urlParams.get('batch');
        }
        
        // Try to find a pattern that looks like a batch ID
        const batchPattern = /TH\d{8}[A-Z0-9]{8}/;
        const match = scannedText.match(batchPattern);
        return match ? match[0] : null;
    }
    
    handleManualSubmit(event) {
        event.preventDefault();
        const batchId = this.elements.batchIdInput.value.trim();
        
        if (batchId) {
            // Validate batch ID format
            if (this.isValidBatchId(batchId)) {
                window.location.href = `/scan/${batchId}`;
            } else {
                this.updateStatus('warning', 'Invalid batch ID format. Please check and try again.');
                this.elements.batchIdInput.focus();
            }
        }
    }
    
    handleSampleClick(event) {
        const batchId = event.target.dataset.batch;
        if (batchId) {
            this.elements.batchIdInput.value = batchId;
            window.location.href = `/scan/${batchId}`;
        }
    }
    
    isValidBatchId(batchId) {
        // Basic validation for batch ID format
        const pattern = /^TH\d{8}[A-Z0-9]{8}$/;
        return pattern.test(batchId);
    }
    
    setButtonStates(scanning) {
        if (this.elements.startButton) {
            this.elements.startButton.style.display = scanning ? 'none' : 'inline-block';
            this.elements.startButton.disabled = scanning;
        }
        
        if (this.elements.stopButton) {
            this.elements.stopButton.style.display = scanning ? 'inline-block' : 'none';
            this.elements.stopButton.disabled = !scanning;
        }
    }
    
    updateStatus(type, message) {
        if (!this.elements.statusDiv) return;
        
        const iconMap = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle',
            secondary: 'stop-circle'
        };
        
        const icon = iconMap[type] || 'info-circle';
        
        this.elements.statusDiv.innerHTML = `
            <div class="alert alert-${type}">
                <i class="fas fa-${icon} me-2"></i>
                ${message}
            </div>
        `;
        
        // Auto-hide non-critical messages
        if (type === 'info' || type === 'secondary') {
            setTimeout(() => {
                if (this.elements.statusDiv.innerHTML.includes(message)) {
                    this.elements.statusDiv.innerHTML = '';
                }
            }, 5000);
        }
    }
    
    showScanSuccess() {
        // Add visual feedback for successful scan
        if (this.elements.reader) {
            this.elements.reader.style.border = '3px solid #22c55e';
            this.elements.reader.style.boxShadow = '0 0 20px rgba(34, 197, 94, 0.5)';
            
            setTimeout(() => {
                this.elements.reader.style.border = '3px solid rgb(34, 197, 94)';
                this.elements.reader.style.boxShadow = 'none';
            }, 2000);
        }
        
        // Play success sound (if available)
        this.playSuccessSound();
    }
    
    playSuccessSound() {
        try {
            // Create a simple success beep
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            // Silently fail if audio context is not supported
        }
    }
    
    handleScannerError(error) {
        let message = 'Scanner error occurred.';
        
        if (error.name === 'NotAllowedError') {
            message = 'Camera access denied. Please allow camera permissions and try again.';
        } else if (error.name === 'NotFoundError') {
            message = 'No camera found. Please connect a camera and try again.';
        } else if (error.name === 'NotSupportedError') {
            message = 'Camera not supported on this device. Please try manual entry.';
        } else if (error.name === 'NotReadableError') {
            message = 'Camera is already in use by another application.';
        } else if (error.name === 'OverconstrainedError') {
            message = 'Camera constraints cannot be satisfied.';
        }
        
        this.updateStatus('danger', message);
    }
    
    // Cleanup method
    destroy() {
        if (this.isScanning) {
            this.stopScanner();
        }
        
        // Remove event listeners
        document.removeEventListener('visibilitychange', this.visibilityChangeHandler);
        window.removeEventListener('resize', this.resizeHandler);
    }
}

// Initialize QR Scanner when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on QR scanner page
    if (document.getElementById('qr-reader')) {
        window.qrScanner = new TrustHarvestQRScanner();
        
        // Handle page unload
        window.addEventListener('beforeunload', function() {
            if (window.qrScanner) {
                window.qrScanner.destroy();
            }
        });
    }
});

// Export for use in other scripts
window.TrustHarvestQRScanner = TrustHarvestQRScanner;
