document.addEventListener("DOMContentLoaded", function() {
    // Toggle custom settings based on selected document type.
    document.getElementsByName("doc_type").forEach(radio => {
      radio.addEventListener("change", function() {
        const customSettings = document.getElementById("customSettings");
        if (this.value === "custom") {
          customSettings.style.display = "block";
        } else {
          customSettings.style.display = "none";
        }
      });
    });
    
    function uploadAndAnalyze() {
      const fileInput = document.getElementById("fileInput");
      if (fileInput.files.length === 0) {
        alert("I guess you are drunk! Please select a file before uploading.");
        return; // Prevent further execution
      }
    
      // Check if a document type is selected.
      const docType = document.querySelector('input[name="doc_type"]:checked');
      if (!docType) {
        alert("Comeon! Please select an Analysis mode.");
        return; // Stop execution if no document type is selected.
      }
    
      // Check if a JSON output mode is selected.
      const jsonMode = document.querySelector('input[name="json_mode"]:checked');
      if (!jsonMode) {
        alert("Please select a JSON Output Mode.");
        return;
      }
    
      const form = document.getElementById("uploadForm");
      const formData = new FormData(form);
      const xhr = new XMLHttpRequest();
    
      const progressBarContainer = document.getElementById("progressBarContainer");
      const progressBar = document.getElementById("progressBar");
      const progressText = document.getElementById("progressText");
      const processingMessage = document.getElementById("processingMessage");
      const execTimeDiv = document.getElementById("execTime");
    
      progressBarContainer.style.display = "block";
      const processingTimeout = setTimeout(() => {
        processingMessage.style.display = "block";
      }, 500);
    
      xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          progressBar.style.width = percentComplete + "%";
          progressText.textContent = percentComplete + "%";
        }
      };
    
      xhr.onload = function() {
        clearTimeout(processingTimeout);
        processingMessage.style.display = "none";
        if (xhr.status === 200) {
          const data = JSON.parse(xhr.responseText);
          if (data.execution_time) {
            execTimeDiv.innerText = "Execution Time: " + data.execution_time + " seconds";
            execTimeDiv.style.display = "block";
          }
          if (data.redirect) {
            window.open(data.redirect, "_blank");
          }
          setTimeout(() => {
            progressBar.style.width = "0%";
            progressText.textContent = "0%";
            progressBarContainer.style.display = "none";
          }, 1000);
        } else {
          console.error("Upload failed with status", xhr.status);
          progressBarContainer.style.display = "none";
        }
      };
    
      xhr.onerror = function() {
        clearTimeout(processingTimeout);
        console.error("An error occurred during the upload.");
        progressBarContainer.style.display = "none";
        processingMessage.style.display = "none";
      };
    
      xhr.open("POST", "/upload", true);
      xhr.send(formData);
    }
    
    // Expose uploadAndAnalyze to the global scope if needed, so your HTML can call it.
    window.uploadAndAnalyze = uploadAndAnalyze;
  });
  