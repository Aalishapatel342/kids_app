let selectedShape = null;

/* =========================
   ADD SHAPE
========================= */
function addShape(type) {
    const canvas = document.getElementById("shapeCanvas");
    const shape = document.createElement("div");

    shape.className = "shape " + type;
    shape.dataset.type = type;
    shape.dataset.color = "#51cf66";

    const size = 80;
    shape.style.left = Math.random() * 600 + "px";
    shape.style.top = Math.random() * 300 + "px";

    if (type !== "triangle") {
        shape.style.width = size + "px";
        shape.style.height = size + "px";
        shape.style.backgroundColor = shape.dataset.color;
    } else {
        shape.style.borderLeft = size / 2 + "px solid transparent";
        shape.style.borderRight = size / 2 + "px solid transparent";
        shape.style.borderBottom = size + "px solid " + shape.dataset.color;
    }

    makeDraggable(shape);
    canvas.appendChild(shape);
}

/* =========================
   DRAG LOGIC
========================= */
function makeDraggable(el) {
    let isDragging = false;
    let startX, startY, initialLeft, initialTop;

    el.onmousedown = function (e) {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        initialLeft = parseInt(el.style.left);
        initialTop = parseInt(el.style.top);

        document.onmousemove = function (e) {
            if (!isDragging) return;
            el.style.left = (initialLeft + e.clientX - startX) + "px";
            el.style.top = (initialTop + e.clientY - startY) + "px";
        };

        document.onmouseup = function () {
            isDragging = false;

            document.onmousemove = null;
            document.onmouseup = null;
        };
    };

    el.ondblclick = function (e) {
        e.stopPropagation();
        editShape(el);
    };
}

/* =========================
   EDIT PANEL
========================= */
function createEditPanel() {
    const panel = document.createElement("div");
    panel.id = "editPanel";
    panel.style.position = "absolute";
    panel.style.display = "none";
    panel.style.background = "#fff";
    panel.style.border = "1px solid #333";
    panel.style.padding = "10px";
    panel.style.zIndex = "1000";

    panel.innerHTML = `
        <label>Color:
            <input type="color" id="colorInput">
        </label><br><br>
        <label>Size:
            <input type="number" id="sizeInput" min="40" max="140">
        </label><br><br>
        <button id="applyBtn">Apply</button>
        <button id="cancelBtn">Cancel</button>
    `;

    document.body.appendChild(panel);
    return panel;
}

function editShape(shape) {
    let panel = document.getElementById("editPanel");
    if (!panel) panel = createEditPanel();

    const colorInput = document.getElementById("colorInput");
    const sizeInput = document.getElementById("sizeInput");

    colorInput.value = shape.dataset.color;
    sizeInput.value = shape.dataset.type === "triangle"
        ? parseInt(shape.style.borderBottomWidth)
        : shape.offsetWidth;

    panel.style.left = (shape.offsetLeft + 40) + "px";
    panel.style.top = (shape.offsetTop + 40) + "px";
    panel.style.display = "block";

    document.getElementById("applyBtn").onclick = function () {
        const color = colorInput.value;
        const size = Math.min(140, Math.max(40, parseInt(sizeInput.value)));

        shape.dataset.color = color;

        if (shape.dataset.type === "triangle") {
            shape.style.borderLeft = size / 2 + "px solid transparent";
            shape.style.borderRight = size / 2 + "px solid transparent";
            shape.style.borderBottom = size + "px solid " + color;
        } else {
            shape.style.width = size + "px";
            shape.style.height = size + "px";
            shape.style.backgroundColor = color;
        }

        panel.style.display = "none";
    };

    document.getElementById("cancelBtn").onclick = function () {
        panel.style.display = "none";
    };
}

/* =========================
   CLEAR CANVAS
========================= */
function clearCanvas() {
    document.getElementById("shapeCanvas").innerHTML = "";
}

/* =========================
   FINISH WORK
========================= */
function finishWork() {
    if (typeof TARGET_KEY === "undefined") {
        alert("Target not loaded. Please refresh.");
        return;
    }

    const shapes = [];
    document.querySelectorAll(".shape").forEach(s => {
        shapes.push(s.dataset.type);
    });

    console.log("Shapes sent:", shapes);
    console.log("Target sent:", TARGET_KEY);

    fetch("/check_shape", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            shapes: shapes,
            target: TARGET_KEY
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            location.reload();
        }
    })
    .catch(err => {
        console.error("Fetch error:", err);
        alert("Server error");
    });
}
