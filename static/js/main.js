// TrustHarvest - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeTooltips();
    initializeAlerts();
    initializeModals();
    initializeFormValidation();
    initializeImagePreviews();
    initializeCopyToClipboard();
    
    console.log('TrustHarvest application initialized successfully');
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Initialize auto-dismissing alerts
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Initialize modals
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function (event) {
            // Clear any previous form errors when modal opens
            const form = this.querySelector('form');
            if (form) {
                clearFormErrors(form);
            }
        });
    });
}

// Form validation helpers
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function clearFormErrors(form) {
    const invalidInputs = form.querySelectorAll('.is-invalid');
    const invalidFeedback = form.querySelectorAll('.invalid-feedback');
    
    invalidInputs.forEach(input => input.classList.remove('is-invalid'));
    invalidFeedback.forEach(feedback => feedback.style.display = 'none');
}

// Image preview functionality
function initializeImagePreviews() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(event) {
            handleImagePreview(event, input);
        });
    });
}

function handleImagePreview(event, input) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Create or update preview element
            let preview = input.parentNode.querySelector('.image-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'image-preview mt-2';
                input.parentNode.appendChild(preview);
            }
            
            preview.innerHTML = `
                <img src="${e.target.result}" 
                     alt="Preview" 
                     class="img-thumbnail" 
                     style="max-width: 200px; max-height: 200px;">
                <div class="mt-1">
                    <small class="text-muted">${file.name} (${formatFileSize(file.size)})</small>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Copy to clipboard functionality
function initializeCopyToClipboard() {
    document.addEventListener('click', function(event) {
        if (event.target.matches('[data-copy]') || event.target.closest('[data-copy]')) {
            const button = event.target.closest('[data-copy]') || event.target;
            const textToCopy = button.dataset.copy || button.textContent;
            
            copyToClipboard(textToCopy, button);
        }
    });
}

async function copyToClipboard(text, button) {
    try {
        await navigator.clipboard.writeText(text);
        showCopySuccess(button);
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showCopySuccess(button);
        } catch (fallbackErr) {
            console.error('Failed to copy text: ', fallbackErr);
            showCopyError(button);
        }
        document.body.removeChild(textArea);
    }
}

function showCopySuccess(button) {
    const originalContent = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i>';
    button.classList.add('btn-success');
    button.classList.remove('btn-outline-secondary');
    
    setTimeout(() => {
        button.innerHTML = originalContent;
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-secondary');
    }, 2000);
}

function showCopyError(button) {
    const originalContent = button.innerHTML;
    button.innerHTML = '<i class="fas fa-times"></i>';
    button.classList.add('btn-danger');
    
    setTimeout(() => {
        button.innerHTML = originalContent;
        button.classList.remove('btn-danger');
    }, 2000);
}

// Loading state management
function showLoading(element, message = 'Loading...') {
    element.classList.add('loading');
    element.setAttribute('data-original-content', element.innerHTML);
    element.innerHTML = `
        <i class="fas fa-spinner fa-spin me-2"></i>${message}
    `;
    element.disabled = true;
}

function hideLoading(element) {
    element.classList.remove('loading');
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
        element.innerHTML = originalContent;
        element.removeAttribute('data-original-content');
    }
    element.disabled = false;
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search');
    const searchForm = searchInput?.closest('form');
    
    if (searchInput && searchForm) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    searchForm.submit();
                }
            }, 500);
        });
    }
}

// Geolocation functionality
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by this browser.'));
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            error => {
                let errorMessage;
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Location access denied by user.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Location information is unavailable.';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Location request timed out.';
                        break;
                    default:
                        errorMessage = 'An unknown error occurred.';
                        break;
                }
                reject(new Error(errorMessage));
            }
        );
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// Debounce function for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

// Theme management
function initializeTheme() {
    const savedTheme = localStorage.getItem('trustharvest-theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('trustharvest-theme', newTheme);
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    // Could send to error reporting service
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    // Could send to error reporting service
});

// Export functions for use in other scripts
window.TrustHarvest = {
    showLoading,
    hideLoading,
    copyToClipboard,
    getCurrentLocation,
    formatCurrency,
    formatDate,
    debounce,
    toggleTheme
};

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Performance monitoring
function logPerformanceMetrics() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
            }, 0);
        });
    }
}

// Initialize performance monitoring
logPerformanceMetrics();
