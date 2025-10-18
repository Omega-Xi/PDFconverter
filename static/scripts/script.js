const inputLabel = document.getElementById("inputLabel");
const pdfInput = document.getElementById("pdfInput");
const downloadLabel = document.getElementById("downloadLabel");
const downloadBtn = document.getElementById("downloadBtn");
const spinner = document.getElementById("spinner");
let fileName = null;
let convertedFile = null;
const uploadDiv = document.getElementById("uploadDiv");

// Drag and drop setup
uploadDiv.addEventListener('dragover', e => {
    e.preventDefault();
});

uploadDiv.addEventListener('drop', e => {
    e.preventDefault();
    if (e.dataTransfer.files.length) {
        pdfInput.files = e.dataTransfer.files;
        inputLabel.textContent = `Selected: ${e.dataTransfer.files[0].name}`;
    }
});

// File input change handler
pdfInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        inputLabel.textContent = `Selected: ${this.files[0].name}`;
    }
});

async function startConversion() {
    const pdfFile = pdfInput.files[0];

    if (!pdfFile) {
        alert("Please select a file first!!");
        return;
    }

    // Validate file type
    if (!pdfFile.type.includes('pdf') && !pdfFile.name.toLowerCase().endsWith('.pdf')) {
        alert("Please select a valid PDF file");
        return;
    }

    downloadLabel.textContent = "Converting...";
    downloadBtn.disabled = true;
    spinner.style.display = "flex";
    inputLabel.textContent = `Converting: ${pdfFile.name}`;

    try {
        convertedFile = await convertFile(pdfFile);
        fileName = pdfFile.name;
        
        inputLabel.textContent = `${pdfFile.name} converted successfully!`;
        downloadBtn.disabled = false;
        downloadLabel.textContent = "Click To Download";
        spinner.style.display = "none";
        
    } catch(error) {
        console.error("Conversion error:", error);
        
        let userMessage = "Conversion failed: ";
        if (error.message.includes("Network error")) {
            userMessage += "Unable to connect to server. Please try again later.";
        } else if (error.message.includes("empty file")) {
            userMessage += "Server returned empty file. The PDF might be corrupted or unsupported.";
        } else if (error.message.includes("413")) {
            userMessage += "File too large. Please try a smaller PDF.";
        } else if (error.message.includes("415")) {
            userMessage += "Unsupported file type. Please ensure it's a valid PDF.";
        } else if (error.message.includes("500")) {
            userMessage += "Server error. Please try again later.";
        } else {
            userMessage += error.message;
        }
        
        inputLabel.textContent = userMessage;
        downloadLabel.textContent = "Conversion Failed";
        spinner.style.display = "none";
        downloadBtn.disabled = true;
    }
}

function startDownload() {
    if (!convertedFile) {
        alert("No file to download");
        return;
    }

    const url = URL.createObjectURL(convertedFile);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName.replace(/\.pdf$/i, ".txt");
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // Reset UI
    inputLabel.textContent = "Upload your PDF here";
    downloadBtn.disabled = true;
    downloadLabel.textContent = "";
    pdfInput.value = "";
    convertedFile = null;
    fileName = null;
}

async function convertFile(pdfFile) {
    const formData = new FormData();
    formData.append('pdf', pdfFile);

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorMessage = `Server Error: ${response.status} ${response.statusText}`;
            
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If response isn't JSON, use status text
                const errorText = await response.text();
                console.log('Raw error response:', errorText);
            }
            
            throw new Error(errorMessage);
        }

        const blob = await response.blob();
        
        if (blob.size === 0) {
            throw new Error("Server returned empty file");
        }

        return blob;

    } catch (error) {
        console.error("File conversion failed:", error);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error("Network error - check your connection and server status");
        }
        
        throw error;
    }
}

// Check if server is reachable
async function checkServerStatus() {
    try {
        const response = await fetch('/health', {
            method: 'GET'
        });
        
        if (response.ok) {
            console.log('Server is reachable');
            return true;
        } else {
            console.warn('Server responded with error status:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Server is not reachable:', error);
        return false;
    }
}

// Call this on page load
window.addEventListener('load', async () => {
    const isServerUp = await checkServerStatus();
    if (!isServerUp) {
        inputLabel.textContent = "Warning: Server connection issues detected";
    }
});