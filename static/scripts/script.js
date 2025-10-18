const inputLabel=document.getElementById("inputLabel");
const pdfInput=document.getElementById("pdfInput");
const downloadLabel=document.getElementById("downloadLabel");
const downloadBtn=document.getElementById("downloadBtn");
const spinner=document.getElementById("spinner");
let fileName=null;
let convertedFile=null;//used to store the return file
const uploadDiv=document.getElementById("uploadDiv");

//optional drag and drop setup
uploadDiv.addEventListener('dragover',e=>{

    //to stop from file opening in browser
    e.preventDefault();
});

//changing input file on drop
uploadDiv.addEventListener('drop',e=>{

    //to stop from file opening in browser
    e.preventDefault();
    //checking if any files were dragged
    if(e.dataTransfer.files.length){
        pdfInput.files=e.dataTransfer.files;
    }
});

async function startConversion(){
    const pdfFile = pdfInput.files[0];

    if(!pdfFile) {
        alert("Please select a file first!!");
        return;
    }

    // Validate file type
    if (!pdfFile.type.includes('pdf') && !pdfFile.name.toLowerCase().endsWith('.pdf')) {
        alert("Please select a valid PDF file");
        return;
    }

    // Update UI
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
        
        // User-friendly error messages
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
function startDownload(){
    //creating url for converted file
    const url=URL.createObjectURL(convertedFile);

    //link element for download
    const a=document.createElement("a");
    a.href=url;
    a.download = fileName.replace(/\.pdf$/i, ".txt");//setting download name

    //adding and removing link to ensure functionality on all browsers
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);//clean up

    //resetting components
    inputLabel.textContent=`Upload your PDF here`;
    downloadBtn.disabled=true;
    downloadLabel.textContent="";
    pdfInput.value="";
}
async function convertFile(pdfFile) {
    const formData = new FormData();
    formData.append('pdf', pdfFile);

    try {
        // Use absolute path for deployment compatibility
        const response = await fetch('/convert', { // Changed from '/' to specific endpoint
            method: 'POST',
            body: formData,
            // Add headers for better debugging
            headers: {
                'Accept': 'application/json, text/plain, */*',
            }
        });

        // Enhanced error handling
        if (!response.ok) {
            // Try to get detailed error message from response
            let errorMessage = `Server Error: ${response.status} ${response.statusText}`;
            
            try {
                const errorText = await response.text();
                if (errorText) {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.error || errorData.message || errorText;
                }
            } catch (e) {
                // If response isn't JSON, use status text
                console.log('Raw error response:', await response.text());
            }
            
            throw new Error(errorMessage);
        }

        // Check if response is valid
        const blob = await response.blob();
        
        if (blob.size === 0) {
            throw new Error("Server returned empty file");
        }

        return blob;

    } catch (error) {
        console.error("File conversion failed:", {
            error: error.message,
            fileName: pdfFile.name,
            fileSize: pdfFile.size,
            fileType: pdfFile.type
        });
        
        // More specific error messages for common issues
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
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
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

// Call this on page load or before conversion
window.addEventListener('load', async () => {
    const isServerUp = await checkServerStatus();
    if (!isServerUp) {
        inputLabel.textContent = "Warning: Server connection issues detected";
    }
});