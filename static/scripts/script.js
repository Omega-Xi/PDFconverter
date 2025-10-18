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
    //Get the selected file
    const pdfFile=pdfInput.files[0];

    //Checking if file is present
    if(!pdfFile)
    {
        alert("Please select a file first!!");
        return;
    }
    downloadLabel.textContent="Please wait...";
    spinner.style.display="flex";
    //Calling convert function to pass file to python converter
    try{
        convertedFile=await convertFile(pdfFile);
        fileName=pdfFile.name;
        inputLabel.textContent=`${pdfFile.name} has been converted`;
        downloadBtn.disabled=false;
        downloadLabel.textContent="Click To Download";
        spinner.style.display="none";
    }
    catch(error){
        inputLabel.textContent=error;
        downloadLabel.textContent="Conversion Failed";
        spinner.style.display="none";
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
async function convertFile(pdfFile){
    //used to wrap PDF for transmission
    const formData= new FormData();
    //wrapping file
    formData.append('pdf',pdfFile);

    //sending the file to backend code
    try{
        const response=await fetch('/',{method:'POST',body:formData});
        //checking if file fetched successfully
        if(!response.ok){
            throw new Error("Server Returned Error");
        }
        
        //storing file in temporarily
        const blob= await response.blob();
        return blob;
    }
    catch(error){
        console.error("File fetching failed:",error);
        alert("Something Went Wrong");
        throw error;
    }

}