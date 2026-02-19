// results.js

// Global object to track counters for drag boxes per page.
const boxCounters = {};

// Setup each page once the image loads.
function setupPage(pageIndex) {
  // Initialize counter for page if not set.
  if (!boxCounters[pageIndex]) {
    boxCounters[pageIndex] = 1;
  }
  // Setup initial drag box for the page.
  setupDragBox(pageIndex, 1);
  
  // Set container dimensions from the processed image.
  const img = document.getElementById("processedImage_" + pageIndex);
  const container = document.getElementById("annotationContainer_" + pageIndex);
  img.onload = () => {
    container.style.width = img.clientWidth + "px";
    container.style.height = img.clientHeight + "px";
  };
}

// Wait for the document to load and then initialize all pages.
document.addEventListener('DOMContentLoaded', function() {
  for (let pageIndex = 1; pageIndex <= numPages; pageIndex++) {
    setupPage(pageIndex);
  }
});

// Setup event listeners for a drag box.
function setupDragBox(pageIndex, boxId) {
  const container = document.getElementById("annotationContainer_" + pageIndex);
  const dragBox = document.getElementById("dragBox_" + pageIndex + "_" + boxId);
  const coordDisplay = document.getElementById("coordDisplay_" + pageIndex + "_" + boxId);
  const resizeHandle = document.getElementById("resizeHandle_" + pageIndex + "_" + boxId);

  // DRAGGING:
  let isDragging = false, offsetX = 0, offsetY = 0;
  dragBox.addEventListener("mousedown", function(e) {
    // Prevent dragging when clicking on the resize handle or delete button.
    if (e.target.classList.contains("resize-handle") || e.target.classList.contains("delete-box"))
      return;
    isDragging = true;
    offsetX = e.offsetX;
    offsetY = e.offsetY;
  });
  
  document.addEventListener("mousemove", function(e) {
    if (!isDragging) return;
    e.preventDefault();
    const containerRect = container.getBoundingClientRect();
    let newLeft = e.clientX - containerRect.left - offsetX;
    let newTop = e.clientY - containerRect.top - offsetY;
    newLeft = Math.max(0, Math.min(newLeft, containerRect.width - dragBox.offsetWidth));
    newTop = Math.max(0, Math.min(newTop, containerRect.height - dragBox.offsetHeight));
    dragBox.style.left = newLeft + "px";
    dragBox.style.top = newTop + "px";
    updateCoordDisplay(pageIndex, boxId);
  });
  
  document.addEventListener("mouseup", () => isDragging = false);

  // RESIZING:
  let isResizing = false, startWidth, startHeight, startMouseX, startMouseY;
  resizeHandle.addEventListener("mousedown", function(e) {
    e.stopPropagation();
    isResizing = true;
    startMouseX = e.clientX;
    startMouseY = e.clientY;
    const rect = dragBox.getBoundingClientRect();
    startWidth = rect.width;
    startHeight = rect.height;
  });
  
  document.addEventListener("mousemove", function(e) {
    if (!isResizing) return;
    e.preventDefault();
    const dx = e.clientX - startMouseX;
    const dy = e.clientY - startMouseY;
    let newWidth = startWidth + dx;
    let newHeight = startHeight + dy;
    newWidth = newWidth < 20 ? 20 : newWidth;
    newHeight = newHeight < 20 ? 20 : newHeight;
    const containerRect = container.getBoundingClientRect();
    const currentLeft = parseFloat(dragBox.style.left) || 0;
    const currentTop  = parseFloat(dragBox.style.top) || 0;
    newWidth = Math.min(newWidth, containerRect.width - currentLeft);
    newHeight = Math.min(newHeight, containerRect.height - currentTop);
    dragBox.style.width = newWidth + "px";
    dragBox.style.height = newHeight + "px";
    updateCoordDisplay(pageIndex, boxId);
  });
  
  document.addEventListener("mouseup", () => isResizing = false);

  // Update the coordinate display based on the drag box position.
  function updateCoordDisplay(pageIndex, boxId) {
    const rect = dragBox.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    const dispX = Math.round(rect.left - containerRect.left);
    const dispY = Math.round(rect.top - containerRect.top);
    const { scaleX, scaleY } = getScaleFactorsByPage(pageIndex);
    const rawX = Math.round(dispX * scaleX);
    const rawY = Math.round(dispY * scaleY);
    coordDisplay.innerText = `x: ${rawX}, y: ${rawY}`;
  }
}

// Get scaling factors for an image on a given page.
function getScaleFactorsByPage(pageIndex) {
  const img = document.getElementById("processedImage_" + pageIndex);
  return {
    scaleX: img.naturalWidth / img.clientWidth,
    scaleY: img.naturalHeight / img.clientHeight
  };
}

// Add a new drag box to a given page.
function addDragBox(pageIndex) {
  boxCounters[pageIndex] = (boxCounters[pageIndex] || 1) + 1;
  const newBoxId = boxCounters[pageIndex];
  const container = document.getElementById("annotationContainer_" + pageIndex);
  const newBox = document.createElement("div");
  newBox.className = "dragBox";
  newBox.id = "dragBox_" + pageIndex + "_" + newBoxId;
  newBox.style.left = "30px";
  newBox.style.top = "30px";
  newBox.style.width = "150px";
  newBox.style.height = "80px";
  
  const newCoordDisplay = document.createElement("div");
  newCoordDisplay.className = "coordDisplay";
  newCoordDisplay.id = "coordDisplay_" + pageIndex + "_" + newBoxId;
  newCoordDisplay.innerText = "x: 30, y: 30";
  newBox.appendChild(newCoordDisplay);
  
  const newResizeHandle = document.createElement("div");
  newResizeHandle.className = "resize-handle";
  newResizeHandle.id = "resizeHandle_" + pageIndex + "_" + newBoxId;
  newBox.appendChild(newResizeHandle);
  
  const newDeleteBtn = document.createElement("button");
  newDeleteBtn.className = "delete-box";
  newDeleteBtn.innerText = "×";
  newDeleteBtn.onclick = function() { deleteBox(pageIndex, newBoxId); };
  newBox.appendChild(newDeleteBtn);
  
  container.appendChild(newBox);
  setupDragBox(pageIndex, newBoxId);
}

// Delete a drag box.
function deleteBox(pageIndex, boxId) {
  const box = document.getElementById("dragBox_" + pageIndex + "_" + boxId);
  if (box) {
    box.remove();
  }
}

// Copy coordinates for all drag boxes on a given page.
function copyAllCoordinates(pageIndex) {
  const container = document.getElementById("annotationContainer_" + pageIndex);
  const boxes = container.querySelectorAll(".dragBox");
  const { scaleX, scaleY } = getScaleFactorsByPage(pageIndex);
  let allCoords = [];
  boxes.forEach(box => {
    const rect = box.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    const dispX = Math.round(rect.left - containerRect.left);
    const dispY = Math.round(rect.top - containerRect.top);
    const dispW = rect.width;
    const dispH = rect.height;
    const rawX = Math.round(dispX * scaleX);
    const rawY = Math.round(dispY * scaleY);
    const rawW = Math.round(dispW * scaleX);
    const rawH = Math.round(dispH * scaleY);
    const corners = {
      top_left: [rawX, rawY],
      top_right: [rawX + rawW, rawY],
      bottom_left: [rawX, rawY + rawH],
      bottom_right: [rawX + rawW, rawY + rawH]
    };
    allCoords.push({
      "text": "",
      "x": rawX,
      "y": rawY,
      "width": rawW,
      "height": rawH,
      "corners": corners
    });
  });
  const jsonString = JSON.stringify(allCoords, null, 4);
  navigator.clipboard.writeText(jsonString)
    .then(() => {
      alert("All box coordinates copied to clipboard for Page " + pageIndex + ":\n" + jsonString);
    })
    .catch(err => {
      console.error("Error copying coordinates:", err);
      alert("Error copying coordinates. Check console for details.");
    });
}
