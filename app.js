// ===================================
// TOM CITY EDITION - APP.JS
// Built by: html-ramu
// ===================================

// CONFIGURATION
const REPO_URL = "https://tom-city-edition.in"; 

// ===================================
// EDITION DATA
// ===================================
// Each edition entry format: "DD-MM-YYYY": { pages: X, pdf: "full.pdf" }

const editions = {
    // ROBOT_ENTRY_POINT
    "08-02-2026": { pages: 5, pdf: "full.pdf" },
    "07-02-2026": { pages: 5, pdf: "full.pdf" },
};

// ===================================
// HELPER FUNCTIONS
// ===================================

/**
 * Sort edition dates (Newest First)
 * Converts DD-MM-YYYY strings to Date objects for proper sorting
 */
function getSortedDates() {
    return Object.keys(editions).sort((a, b) => {
        const [d1, m1, y1] = a.split('-').map(Number);
        const [d2, m2, y2] = b.split('-').map(Number);
        const dateA = new Date(y1, m1 - 1, d1);
        const dateB = new Date(y2, m2 - 1, d2);
        return dateB - dateA; // Newest first
    });
}

// ===================================
// STATE MANAGEMENT
// ===================================

let currentDateStr = "";  // Currently viewing edition (DD-MM-YYYY)
let currentPage = 1;      // Current page number
let totalPages = 1;       // Total pages in current edition
let cropper = null;       // Cropper.js instance for clipper tool

// ===================================
// INITIALIZATION
// ===================================

window.onload = function() {
    setupDateDisplay();
    
    // Close modals when clicking outside
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    }
    
    // Logo click - refresh/go to home
    const logoClick = document.getElementById('logoClick');
    if (logoClick) {
        logoClick.addEventListener('click', function() {
            window.location.reload();
        });
    }
};

// ===================================
// DATE & EDITION LOADING
// ===================================

/**
 * Initialize date display and load the newest edition
 */
function setupDateDisplay() {
    const today = new Date();
    const d = String(today.getDate()).padStart(2, '0');
    const m = String(today.getMonth() + 1).padStart(2, '0');
    const y = today.getFullYear();
    const todayStr = `${d}-${m}-${y}`;
    
    // Get sorted edition dates (newest first)
    const sortedDates = getSortedDates();
    
    if (sortedDates.length > 0) {
        // Load the newest edition available
        currentDateStr = sortedDates[0];
        loadEdition(currentDateStr);
        populateDateDropdown();
    } else {
        // No editions published yet
        showNoEditionsMessage();
    }
}

/**
 * Display message when no editions are available
 */
function showNoEditionsMessage() {
    document.getElementById('liveDate').innerText = "Coming Soon";
    document.getElementById('pageIndicator').innerText = "No Editions Yet";
    document.getElementById('btnPrev').disabled = true;
    document.getElementById('btnNext').disabled = true;
    document.getElementById('btnPdf').style.display = 'none';
    document.getElementById('btnCut').disabled = true;
    
    const viewerContainer = document.getElementById('viewerContainer');
    viewerContainer.innerHTML = '<div id="loadingMsg">📰 First edition coming soon! Check back later.</div>';
}

/**
 * Load a specific edition by date
 * @param {string} dateStr - Date in DD-MM-YYYY format
 */
function loadEdition(dateStr) {
    if (!editions[dateStr]) {
        console.error(`Edition ${dateStr} not found`);
        return;
    }

    currentDateStr = dateStr;
    currentPage = 1;
    totalPages = editions[dateStr].pages;
    
    // Update date display
    document.getElementById('liveDate').innerText = dateStr;
    
    // Setup PDF download button
    setupPDFButton();
    
    // Load first page
    updateViewer();
}

/**
 * Setup PDF download button with correct link
 */
function setupPDFButton() {
    const pdfBtn = document.getElementById('btnPdf');
    if (pdfBtn) {
        const pdfUrl = `papers/${currentDateStr}/full.pdf`;
        pdfBtn.href = pdfUrl;
        pdfBtn.setAttribute("download", `Tom-City-Edition-${currentDateStr}.pdf`);
        pdfBtn.target = "_blank";
        pdfBtn.style.display = "inline-block";
        pdfBtn.innerText = "PDF";
    }
}

/**
 * Update the viewer to show current page
 */
function updateViewer() {
    const imgPath = `papers/${currentDateStr}/${currentPage}.png`;
    const imgElement = document.getElementById('pageImage');
    const indicator = document.getElementById('pageIndicator');
    
    // Fade effect while loading
    imgElement.style.opacity = "0.5";
    imgElement.src = imgPath;
    indicator.innerText = `Page ${currentPage} / ${totalPages}`;

    // Restore opacity when loaded
    imgElement.onload = function() {
        imgElement.style.opacity = "1";
    };
    
    imgElement.onerror = function() {
        imgElement.style.opacity = "1";
        console.error(`Failed to load: ${imgPath}`);
    };

    // Update navigation buttons
    updateNavigationButtons();
}

/**
 * Enable/disable navigation buttons based on current page
 */
function updateNavigationButtons() {
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');
    
    // Previous buttons
    if (currentPage === 1) {
        btnPrev.disabled = true;
        if (leftArrow) leftArrow.disabled = true;
    } else {
        btnPrev.disabled = false;
        if (leftArrow) leftArrow.disabled = false;
    }
    
    // Next buttons
    if (currentPage === totalPages) {
        btnNext.disabled = true;
        if (rightArrow) rightArrow.disabled = true;
    } else {
        btnNext.disabled = false;
        if (rightArrow) rightArrow.disabled = false;
    }
}

// ===================================
// PAGE NAVIGATION
// ===================================

/**
 * Change page (previous/next)
 * @param {number} delta - -1 for previous, +1 for next
 */
function changePage(delta) {
    const newPage = currentPage + delta;
    
    if (newPage >= 1 && newPage <= totalPages) {
        // Play page flip sound
        playPageFlipSound();
        
        // Update page
        currentPage = newPage;
        updateViewer();
        
        // Scroll to top of viewer
        window.scrollTo({
            top: 120,
            behavior: 'smooth'
        });
    }
}

/**
 * Play page flip sound effect
 */
function playPageFlipSound() {
    try {
        const audio = new Audio('assets/page-flip-4.mp3');
        audio.volume = 0.4;
        audio.play().catch(e => {
            console.log("Audio playback requires user interaction");
        });
    } catch (err) {
        console.log("Audio error:", err);
    }
}

/**
 * Reset viewer to first page of current edition
 */
function resetViewer() {
    if (currentDateStr && editions[currentDateStr]) {
        currentPage = 1;
        updateViewer();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// ===================================
// MENU & UI INTERACTIONS
// ===================================

/**
 * Toggle sidebar menu open/closed
 */
function toggleMenu() {
    const sidebar = document.getElementById("sidebar");
    sidebar.style.width = (sidebar.style.width === "250px") ? "0" : "250px";
}

/**
 * Set active category in category bar
 * @param {HTMLElement} element - Clicked category element
 */
function setActive(element) {
    document.querySelectorAll('.cat-item').forEach(item => {
        item.classList.remove('active');
    });
    element.classList.add('active');
}

/**
 * Open information modal (About, Contact, etc.)
 * @param {string} modalId - ID of modal to open
 */
function openInfoModal(modalId) {
    document.getElementById(modalId).style.display = "block";
    // Close sidebar when opening modal
    document.getElementById("sidebar").style.width = "0";
}

/**
 * Close information modal
 * @param {string} modalId - ID of modal to close
 */
function closeInfoModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// ===================================
// EDITION SELECTOR
// ===================================

/**
 * Populate date dropdown with available editions
 */
function populateDateDropdown() {
    const select = document.getElementById('dateSelect');
    if (!select) return;
    
    select.innerHTML = "";
    
    const sortedDates = getSortedDates();
    sortedDates.forEach(date => {
        const option = document.createElement("option");
        option.value = date;
        option.text = date;
        select.appendChild(option);
    });
    
    select.value = currentDateStr;
}

/**
 * Open edition selector modal
 */
function openEditionSelector() {
    const select = document.getElementById('dateSelect');
    if (select) select.value = currentDateStr;
    document.getElementById('editionModal').style.display = "block";
}

/**
 * Close edition selector modal
 */
function closeEditionSelector() {
    document.getElementById('editionModal').style.display = "none";
}

/**
 * Load the selected edition from dropdown
 */
function loadSelectedEdition() {
    const selectedDate = document.getElementById('dateSelect').value;
    loadEdition(selectedDate);
    closeEditionSelector();
}

// ===================================
// CLIPPER TOOL (CROP & SHARE)
// ===================================

/**
 * Toggle clipper overlay open/closed
 */
function toggleClipper() {
    // Prevent clipper if no edition loaded
    if (!cropper && (!currentDateStr || totalPages === 0)) {
        alert("No edition available to clip!");
        return;
    }
    
    const modal = document.getElementById('clipperOverlay');
    const pageImg = document.getElementById('pageImage');
    const clipImg = document.getElementById('clipperImage');
    
    if (modal.style.display === "flex") {
        // Close clipper
        modal.style.display = "none";
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    } else {
        // Open clipper
        modal.style.display = "flex";
        clipImg.src = pageImg.src;
        
        // Initialize Cropper.js after image loads
        setTimeout(() => {
            if (cropper) cropper.destroy();
            cropper = new Cropper(clipImg, {
                viewMode: 1,
                dragMode: 'move',
                autoCropArea: 0.6,
                movable: true,
                zoomable: true,
                scalable: true,
                cropBoxResizable: true,
                cropBoxMovable: true,
                guides: true,
                center: true,
                highlight: true,
                background: true,
            });
        }, 100);
    }
}

/**
 * Create branded canvas with logo, date, and footer
 * @returns {HTMLCanvasElement|null} - Branded canvas or null if error
 */
function getBrandedCanvas() {
    if (!cropper) return null;
    
    const cropCanvas = cropper.getCroppedCanvas();
    if (!cropCanvas) return null;

    // Ensure minimum width for quality
    const minWidth = 600;
    const finalWidth = Math.max(cropCanvas.width, minWidth);
    const scale = finalWidth / 800;

    // Calculate dimensions
    const headerHeight = Math.round(160 * scale);
    const footerHeight = Math.round(110 * scale);
    const finalHeight = cropCanvas.height + headerHeight + footerHeight;

    // Create final canvas
    const finalCanvas = document.createElement('canvas');
    finalCanvas.width = finalWidth;
    finalCanvas.height = finalHeight;
    const ctx = finalCanvas.getContext('2d');

    // Background
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, finalWidth, finalHeight);

    // Draw Logo
    const logoImg = document.querySelector('.logo-area img');
    if (logoImg) {
        const logoH = Math.round(120 * scale);
        const logoW = (logoImg.naturalWidth / logoImg.naturalHeight) * logoH;
        const logoX = (finalWidth - logoW) / 2;
        const logoY = (headerHeight - logoH) / 2;
        ctx.drawImage(logoImg, logoX, logoY, logoW, logoH);
    }

    // Draw Edition Date
    ctx.textAlign = "left";
    ctx.fillStyle = "#333333";
    ctx.font = `bold ${Math.round(20 * scale)}px Arial`;
    ctx.fillText(currentDateStr, 20 * scale, headerHeight / 2 + (8 * scale));

    // Draw Separator Line
    ctx.beginPath();
    ctx.moveTo(20 * scale, headerHeight - 2);
    ctx.lineTo(finalWidth - (20 * scale), headerHeight - 2);
    ctx.strokeStyle = "#eeeeee";
    ctx.lineWidth = 2 * scale;
    ctx.stroke();

    // Draw Cropped Image
    const cropX = (finalWidth - cropCanvas.width) / 2;
    ctx.drawImage(cropCanvas, cropX, headerHeight);

    // Draw Footer Background
    ctx.fillStyle = "#2a2a2a"; // Light black
    ctx.fillRect(0, finalHeight - footerHeight, finalWidth, footerHeight);

    // Draw Footer Text
    ctx.textAlign = "center";
    ctx.fillStyle = "#ffffff";
    
    const fontMain = Math.round(24 * scale);
    ctx.font = `bold ${fontMain}px Arial`;
    ctx.fillText("Read full NEWS at tom-city-edition.in", finalWidth / 2, finalHeight - (footerHeight * 0.6));

    const fontSub = Math.round(16 * scale);
    ctx.font = `normal ${fontSub}px Arial`;
    ctx.fillText("Designed & Developed by html-ramu", finalWidth / 2, finalHeight - (footerHeight * 0.25));

    return finalCanvas;
}

/**
 * Share clipped image (WhatsApp, social media)
 */
async function shareClip() {
    const brandedCanvas = getBrandedCanvas();
    if (!brandedCanvas) {
        alert("Please select an area to clip first!");
        return;
    }
    
    brandedCanvas.toBlob(async (blob) => {
        const file = new File([blob], "tom-city-edition-clip.png", { type: "image/png" });
        
        // Check if Web Share API is available
        if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
            try {
                await navigator.share({
                    files: [file],
                    title: 'Tom City Edition News',
                    text: 'Read full NEWS at tom-city-edition.in'
                });
            } catch (err) {
                console.log("Error sharing:", err);
            }
        } else {
            // Fallback for desktop: download instead
            alert("Sharing is best on Mobile. On Desktop, use 'Download' button.");
            downloadClip();
        }
    });
}

/**
 * Download clipped image
 */
function downloadClip() {
    const brandedCanvas = getBrandedCanvas();
    if (!brandedCanvas) {
        alert("Please select an area to clip first!");
        return;
    }
    
    brandedCanvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Tom-City-Edition-Clip-${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}

// ===================================
// CONSOLE INFO
// ===================================

console.log("%cTom City Edition ePaper", "font-size: 20px; font-weight: bold; color: #2f96f0;");
console.log("%cBuilt by html-ramu", "font-size: 14px; color: #666;");
console.log("%cGitHub: https://github.com/html-ramu", "font-size: 12px; color: #999;");