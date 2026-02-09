class ShapeBuilderGame {
    constructor() {
        this.shapes = [];
        this.selectedShape = null;
        this.currentTask = null;
        this.userId = localStorage.getItem('shapeBuilderUserId') || 'test_user';
        if (!localStorage.getItem('shapeBuilderUserId')) {
            localStorage.setItem('shapeBuilderUserId', this.userId);
        }
        this.selectedColor = '#FF6B6B';
        this.shapeHistory = [];

        this.init();
    }
    
    init() {
        this.loadUserStats();
        this.loadNewTask();
        this.setupEventListeners();
        this.setupDragAndDrop();
    }
    
    setupEventListeners() {
        // Shape palette
        document.querySelectorAll('.shape-option').forEach(option => {
            option.addEventListener('dragstart', this.handleShapeDragStart.bind(this));
        });
        
        // Color palette
        document.querySelectorAll('.color-option').forEach(color => {
            color.addEventListener('click', (e) => {
                document.querySelectorAll('.color-option').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                this.selectedColor = e.target.dataset.color;
                
                if (this.selectedShape) {
                    this.selectedShape.element.style.backgroundColor = this.selectedColor;
                    this.selectedShape.color = this.selectedColor;
                    this.saveToHistory();
                }
            });
        });
        
        // Canvas click
        document.getElementById('canvas').addEventListener('click', (e) => {
            if (e.target === document.getElementById('canvas')) {
                this.deselectAllShapes();
            }
        });
        
        // Control sliders
        document.getElementById('size-slider').addEventListener('input', (e) => {
            const size = e.target.value + 'px';
            document.getElementById('size-value').textContent = size;
            
            if (this.selectedShape) {
                this.selectedShape.element.style.width = size;
                this.selectedShape.element.style.height = size;
                this.selectedShape.size = size;
                this.saveToHistory();
            }
        });
        
        document.getElementById('rotation-slider').addEventListener('input', (e) => {
            const rotation = e.target.value + 'deg';
            document.getElementById('rotation-value').textContent = rotation;
            
            if (this.selectedShape) {
                this.selectedShape.element.style.transform = `rotate(${rotation})`;
                this.selectedShape.rotation = rotation;
                this.saveToHistory();
            }
        });
        
        // Buttons
        document.getElementById('clear-btn').addEventListener('click', () => this.clearCanvas());
        document.getElementById('undo-btn').addEventListener('click', () => this.undo());
        document.getElementById('delete-btn').addEventListener('click', () => this.deleteSelectedShape());
        document.getElementById('done-btn').addEventListener('click', () => this.validateShape());
        document.getElementById('next-btn').addEventListener('click', () => this.loadNewTask());
        
        // Make first color active
        document.querySelector('.color-option').classList.add('active');
    }
    
    setupDragAndDrop() {
        const canvas = document.getElementById('canvas');

        canvas.addEventListener('dragover', (e) => {
            e.preventDefault();
            canvas.style.backgroundColor = 'rgba(74, 84, 225, 0.1)';
        });

        canvas.addEventListener('dragleave', () => {
            canvas.style.backgroundColor = '';
        });

        canvas.addEventListener('drop', (e) => {
            e.preventDefault();
            canvas.style.backgroundColor = '';

            const type = e.dataTransfer.getData('text/plain');
            if (type) {
                const rect = canvas.getBoundingClientRect();
                let x = e.clientX - rect.left;
                let y = e.clientY - rect.top;

                // Clamp to keep shape inside canvas
                const shapeSize = 80;
                x = Math.max(shapeSize/2, Math.min(rect.width - shapeSize/2, x));
                y = Math.max(shapeSize/2, Math.min(rect.height - shapeSize/2, y));

                this.createShape(type, x, y);
            }
        });
    }
    
    handleShapeDragStart(e) {
        e.dataTransfer.setData('text/plain', e.currentTarget.dataset.type);
        e.dataTransfer.effectAllowed = 'copy';
    }
    
    createShape(type, x, y) {
        const shapeId = 'shape_' + Date.now();
        const shape = document.createElement('div');
        shape.className = 'draggable-shape';
        shape.id = shapeId;
        
        // Position at drop point
        shape.style.left = (x - 40) + 'px';
        shape.style.top = (y - 40) + 'px';
        shape.style.width = '80px';
        shape.style.height = '80px';
        shape.style.backgroundColor = this.selectedColor;
        
        // Shape specific styles
        switch(type) {
            case 'circle':
                shape.style.borderRadius = '50%';
                break;
            case 'triangle':
                shape.style.width = '0';
                shape.style.height = '0';
                shape.style.backgroundColor = 'transparent';
                shape.style.borderLeft = '40px solid transparent';
                shape.style.borderRight = '40px solid transparent';
                shape.style.borderBottom = '80px solid ' + this.selectedColor;
                break;
            case 'rectangle':
                shape.style.width = '120px';
                shape.style.height = '60px';
                break;
            // Square is default
        }
        
        shape.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectShape(shapeId);
        });
        
        this.makeDraggable(shape);
        document.getElementById('canvas').appendChild(shape);
        
        const shapeData = {
            id: shapeId,
            type: type,
            element: shape,
            color: this.selectedColor,
            size: type === 'rectangle' ? '120px 60px' : '80px',
            rotation: '0deg',
            position: { x, y }
        };
        
        this.shapes.push(shapeData);
        this.selectShape(shapeId);
        this.saveToHistory();
        
        this.showNotification(`Added ${type} shape!`, 'info');
    }
    
    makeDraggable(element) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        
        element.addEventListener('mousedown', dragMouseDown);
        
        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            e.stopPropagation();
            
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
            element.classList.add('dragging');
        }
        
        const elementDrag = (e) => {
            e = e || window.event;
            e.preventDefault();
            
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            
            element.style.top = (element.offsetTop - pos2) + "px";
            element.style.left = (element.offsetLeft - pos1) + "px";
        }
        
        const closeDragElement = () => {
            document.onmouseup = null;
            document.onmousemove = null;
            element.classList.remove('dragging');

            // Update shape position in data
            const shape = this.shapes.find(s => s.id === element.id);
            if (shape) {
                shape.position = {
                    x: element.offsetLeft + 40,
                    y: element.offsetTop + 40
                };
                this.saveToHistory();
            }
        };
    }
    
    selectShape(shapeId) {
        this.deselectAllShapes();
        
        const shape = this.shapes.find(s => s.id === shapeId);
        if (shape) {
            shape.element.classList.add('selected');
            this.selectedShape = shape;
            
            // Update controls
            const size = parseInt(shape.size) || 80;
            document.getElementById('size-slider').value = size;
            document.getElementById('size-value').textContent = size + 'px';
            
            const rotation = parseInt(shape.rotation) || 0;
            document.getElementById('rotation-slider').value = rotation;
            document.getElementById('rotation-value').textContent = rotation + '°';
        }
    }
    
    deselectAllShapes() {
        this.shapes.forEach(shape => {
            shape.element.classList.remove('selected');
        });
        this.selectedShape = null;
    }
    
    deleteSelectedShape() {
        if (this.selectedShape) {
            const index = this.shapes.findIndex(s => s.id === this.selectedShape.id);
            if (index > -1) {
                this.selectedShape.element.remove();
                this.shapes.splice(index, 1);
                this.saveToHistory();
                this.selectedShape = null;
                this.showNotification('Shape deleted!', 'info');
            }
        }
    }
    
    clearCanvas() {
        if (confirm('Are you sure you want to clear all shapes?')) {
            this.shapes.forEach(shape => shape.element.remove());
            this.shapes = [];
            this.selectedShape = null;
            this.saveToHistory();
            this.showNotification('Canvas cleared!', 'info');
        }
    }
    
    undo() {
        if (this.shapeHistory.length > 1) {
            this.shapeHistory.pop(); // Remove current state
            const previousState = this.shapeHistory[this.shapeHistory.length - 1];
            this.restoreState(previousState);
            this.showNotification('Undo successful!', 'info');
        }
    }
    
    saveToHistory() {
        // Save current state
        const state = this.shapes.map(shape => ({
            ...shape,
            element: null // Don't save DOM element
        }));
        this.shapeHistory.push(JSON.parse(JSON.stringify(state)));
        
        // Limit history size
        if (this.shapeHistory.length > 20) {
            this.shapeHistory.shift();
        }
    }
    
    restoreState(state) {
        // Clear current shapes
        this.shapes.forEach(shape => shape.element.remove());
        this.shapes = [];
        
        // Restore shapes
        state.forEach(shapeData => {
            const shape = document.createElement('div');
            shape.className = 'draggable-shape';
            shape.id = shapeData.id;
            shape.style.left = shapeData.position.x - 40 + 'px';
            shape.style.top = shapeData.position.y - 40 + 'px';
            shape.style.backgroundColor = shapeData.color;
            shape.style.transform = `rotate(${shapeData.rotation})`;
            
            switch(shapeData.type) {
                case 'circle':
                    shape.style.borderRadius = '50%';
                    shape.style.width = shapeData.size;
                    shape.style.height = shapeData.size;
                    break;
                case 'triangle':
                    shape.style.width = '0';
                    shape.style.height = '0';
                    shape.style.backgroundColor = 'transparent';
                    const size = parseInt(shapeData.size);
                    shape.style.borderLeft = (size/2) + 'px solid transparent';
                    shape.style.borderRight = (size/2) + 'px solid transparent';
                    shape.style.borderBottom = size + 'px solid ' + shapeData.color;
                    break;
                case 'rectangle':
                    const [width, height] = shapeData.size.split(' ').map(v => parseInt(v));
                    shape.style.width = width + 'px';
                    shape.style.height = height + 'px';
                    break;
                default:
                    shape.style.width = shapeData.size;
                    shape.style.height = shapeData.size;
            }
            
            shape.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectShape(shapeData.id);
            });
            
            this.makeDraggable(shape);
            document.getElementById('canvas').appendChild(shape);
            
            this.shapes.push({
                ...shapeData,
                element: shape
            });
        });
        
        this.deselectAllShapes();
    }
    
    async loadNewTask() {
        try {
            const response = await fetch(`/api/get_task?user_id=${this.userId}`);
            const task = await response.json();
            
            this.currentTask = task;
            this.updateTaskDisplay(task);
            
            // Clear canvas for new task
            this.clearCanvas();
            
            // Hide next button, show done button
            document.getElementById('next-btn').style.display = 'none';
            document.getElementById('done-btn').style.display = 'flex';
            
            this.showNotification(`New task: ${task.name}!`, 'info');
        } catch (error) {
            console.error('Error loading task:', error);
            this.showNotification('Failed to load task. Please refresh.', 'error');
        }
    }
    
    updateTaskDisplay(task) {
        document.getElementById('task-name').textContent = task.name;
        document.getElementById('task-description').textContent = task.description;
        
        const targetShapes = document.getElementById('target-shapes');
        targetShapes.innerHTML = '';
        
        task.target_shapes.forEach(shape => {
            const div = document.createElement('div');
            div.className = 'target-shape';
            
            const preview = document.createElement('div');
            preview.className = `shape-preview ${shape.type}`;
            
            if (shape.type === 'triangle') {
                preview.style.borderBottomColor = shape.color;
            } else {
                preview.style.backgroundColor = shape.color;
            }
            
            if (shape.size) {
                const size = parseInt(shape.size);
                if (shape.type === 'triangle') {
                    preview.style.borderLeftWidth = (size/2) + 'px';
                    preview.style.borderRightWidth = (size/2) + 'px';
                    preview.style.borderBottomWidth = size + 'px';
                } else {
                    preview.style.width = shape.size;
                    preview.style.height = shape.size;
                }
            }
            
            div.appendChild(preview);
            targetShapes.appendChild(div);
        });
    }
    
    async validateShape() {
        if (this.shapes.length === 0) {
            this.showNotification('Please add at least one shape!', 'error');
            return;
        }

        // Prepare shape data for validation
        const shapeData = this.shapes.map(shape => {
            const rect = shape.element.getBoundingClientRect();
            const canvas = document.getElementById('canvas').getBoundingClientRect();

            const xPercent = ((rect.left + rect.width/2 - canvas.left) / canvas.width * 100).toFixed(0);
            const yPercent = ((rect.top + rect.height/2 - canvas.top) / canvas.height * 100).toFixed(0);

            return {
                type: shape.type,
                color: shape.color,
                position: `${xPercent}% ${yPercent}%`,
                size: shape.size,
                rotation: shape.rotation
            };
        });

        try {
            const response = await fetch('/api/validate_shape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    task_id: this.currentTask.id,
                    shapes: shapeData
                })
            });

            const result = await response.json();

            if (result.valid) {
                this.showNotification(
                    `🎉 ${result.message} You earned ${result.award} coins!`,
                    'success'
                );

                // Update coin display
                this.loadUserStats();

                // Show next button
                document.getElementById('next-btn').style.display = 'flex';
                document.getElementById('done-btn').style.display = 'none';
            } else {
                this.showNotification(`❌ ${result.message} Try again!`, 'error');
            }
        } catch (error) {
            console.error('Validation error:', error);
            this.showNotification('Validation failed. Please try again.', 'error');
        }
    }
    
    async loadUserStats() {
        try {
            const response = await fetch(`/api/user_stats?user_id=${this.userId}`);
            const stats = await response.json();
            
            document.getElementById('coin-count').textContent = stats.coins;
            document.getElementById('completed-tasks').textContent = stats.completed_tasks;
            document.getElementById('total-tasks').textContent = stats.total_tasks;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    showNotification(message, type) {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification show ${type}`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 4000);
    }
}

// Initialize the game when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ShapeBuilderGame();
});