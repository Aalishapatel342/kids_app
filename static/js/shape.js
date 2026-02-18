class ShapeBuilderGame {
    constructor() {
        this.shapes = [];
        this.selectedShape = null;
        this.currentTask = null;
        this.selectedColor = '#FF6B6B';
        this.shapeHistory = [];
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };

        this.init();
    }
    
    async init() {
        const isLoggedIn = await this.checkAuth();
        if (isLoggedIn) {
            this.loadUserStats();
            this.loadNewTask();
            this.setupEventListeners();
            this.setupDragAndDrop();
        }
    }
    
    async checkAuth() {
        try {
            const response = await fetch('/api/user_stats');
            if (response.ok) {
                return true;
            } else {
                window.location.href = '/login';
                return false;
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            window.location.href = '/login';
            return false;
        }
    }
    
    setupEventListeners() {
        // Shape palette - use mousedown instead of dragstart for better control
        document.querySelectorAll('.shape-option').forEach(option => {
            option.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const type = e.currentTarget.dataset.type;
                this.startShapeCreation(type);
            });
        });
        
        // Color palette
        document.querySelectorAll('.color-option').forEach(color => {
            color.addEventListener('click', (e) => {
                document.querySelectorAll('.color-option').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                this.selectedColor = e.target.dataset.color;
                
                if (this.selectedShape) {
                    this.updateShapeColor(this.selectedShape, this.selectedColor);
                }
            });
        });
        
        // Canvas click for deselection
        document.getElementById('canvas').addEventListener('click', (e) => {
            if (e.target === document.getElementById('canvas')) {
                this.deselectAllShapes();
            }
        });
        
        // Control sliders
        document.getElementById('size-slider').addEventListener('input', (e) => {
            const size = e.target.value;
            document.getElementById('size-value').textContent = size + 'px';
            
            if (this.selectedShape) {
                this.updateShapeSize(this.selectedShape, size);
            }
        });
        
        document.getElementById('rotation-slider').addEventListener('input', (e) => {
            const rotation = e.target.value;
            document.getElementById('rotation-value').textContent = rotation + '°';
            
            if (this.selectedShape) {
                this.updateShapeRotation(this.selectedShape, rotation);
            }
        });
        
        // Buttons
        document.getElementById('clear-btn').addEventListener('click', () => this.clearCanvas());
        document.getElementById('undo-btn').addEventListener('click', () => this.undo());
        document.getElementById('delete-btn').addEventListener('click', () => this.deleteSelectedShape());
        document.getElementById('done-btn').addEventListener('click', () => this.validateShape());
        document.getElementById('next-btn').addEventListener('click', () => this.loadNewTask());
        
        // Make first color active
        const firstColor = document.querySelector('.color-option');
        if (firstColor) {
            firstColor.classList.add('active');
        }

        // Add mouse move and up for canvas
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', (e) => this.handleMouseUp(e));
    }
    
    setupDragAndDrop() {
        const canvas = document.getElementById('canvas');
        
        // Remove default drag behavior
        canvas.addEventListener('dragover', (e) => e.preventDefault());
        canvas.addEventListener('drop', (e) => e.preventDefault());
    }
    
    startShapeCreation(type) {
        // Create a preview shape that follows mouse
        this.isCreating = true;
        this.creatingType = type;
        
        const canvas = document.getElementById('canvas');
        canvas.style.cursor = 'crosshair';
        
        // Show instruction
        this.showNotification('Click on canvas to place shape', 'info');
    }
    
    handleMouseMove(e) {
        if (this.isDragging && this.draggedShape) {
            // Handle shape dragging
            e.preventDefault();
            
            const canvas = document.getElementById('canvas');
            const rect = canvas.getBoundingClientRect();
            
            // Calculate new position
            let x = e.clientX - rect.left - this.dragOffset.x;
            let y = e.clientY - rect.top - this.dragOffset.y;
            
            // Constrain to canvas
            const shapeRect = this.draggedShape.element.getBoundingClientRect();
            x = Math.max(0, Math.min(rect.width - shapeRect.width, x));
            y = Math.max(0, Math.min(rect.height - shapeRect.height, y));
            
            // Update position
            this.draggedShape.element.style.left = x + 'px';
            this.draggedShape.element.style.top = y + 'px';
            
            // Update shape data
            this.draggedShape.position = {
                x: x + shapeRect.width/2,
                y: y + shapeRect.height/2
            };
        }
    }
    
    handleMouseUp(e) {
        if (this.isDragging && this.draggedShape) {
            // Finish dragging
            this.isDragging = false;
            this.draggedShape.element.classList.remove('dragging');
            this.draggedShape = null;
            this.saveToHistory();
        }
        
        if (this.isCreating) {
            // Place shape on click
            const canvas = document.getElementById('canvas');
            const rect = canvas.getBoundingClientRect();
            
            if (e.clientX >= rect.left && e.clientX <= rect.right && 
                e.clientY >= rect.top && e.clientY <= rect.bottom) {
                
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                this.createShape(this.creatingType, x, y);
            }
            
            this.isCreating = false;
            canvas.style.cursor = 'default';
        }
    }
    
    createShape(type, x, y) {
        const shapeId = 'shape_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
        const shape = document.createElement('div');
        shape.className = 'draggable-shape';
        shape.id = shapeId;
        shape.dataset.type = type;
        
        // Set initial size
        const initialSize = 60;
        shape.style.width = initialSize + 'px';
        shape.style.height = initialSize + 'px';
        
        // Position (center the shape on click point)
        shape.style.left = (x - initialSize/2) + 'px';
        shape.style.top = (y - initialSize/2) + 'px';
        shape.style.backgroundColor = this.selectedColor;
        shape.style.transform = 'rotate(0deg)';
        
        // Shape specific styles
        if (type === 'circle') {
            shape.style.borderRadius = '50%';
        } else if (type === 'triangle') {
            shape.style.width = '0';
            shape.style.height = '0';
            shape.style.backgroundColor = 'transparent';
            shape.style.borderLeft = (initialSize/2) + 'px solid transparent';
            shape.style.borderRight = (initialSize/2) + 'px solid transparent';
            shape.style.borderBottom = initialSize + 'px solid ' + this.selectedColor;
        } else if (type === 'rectangle') {
            shape.style.width = '90px';
            shape.style.height = '45px';
        }
        
        // Make shape draggable
        this.makeDraggable(shape);
        
        // Add click handler
        shape.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectShape(shapeId);
        });
        
        document.getElementById('canvas').appendChild(shape);
        
        const shapeData = {
            id: shapeId,
            type: type,
            element: shape,
            color: this.selectedColor,
            size: initialSize,
            rotation: 0,
            position: { x, y }
        };
        
        this.shapes.push(shapeData);
        this.selectShape(shapeId);
        this.saveToHistory();
        
        this.showNotification(`Added ${type} shape!`, 'success');
    }
    
    makeDraggable(element) {
        element.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Start dragging
            this.isDragging = true;
            this.draggedShape = this.shapes.find(s => s.id === element.id);
            
            if (this.draggedShape) {
                // Calculate offset from mouse to element corner
                const rect = element.getBoundingClientRect();
                this.dragOffset.x = e.clientX - rect.left;
                this.dragOffset.y = e.clientY - rect.top;
                
                element.classList.add('dragging');
                this.selectShape(element.id);
            }
        });
    }
    
    selectShape(shapeId) {
        this.deselectAllShapes();
        
        const shape = this.shapes.find(s => s.id === shapeId);
        if (shape) {
            shape.element.classList.add('selected');
            this.selectedShape = shape;
            
            // Update controls
            let size = shape.size || 60;
            document.getElementById('size-slider').value = size;
            document.getElementById('size-value').textContent = size + 'px';
            
            let rotation = shape.rotation || 0;
            document.getElementById('rotation-slider').value = rotation;
            document.getElementById('rotation-value').textContent = rotation + '°';
            
            // Update color selection
            if (shape.color) {
                const colorBtn = document.querySelector(`.color-option[data-color="${shape.color}"]`);
                if (colorBtn) {
                    document.querySelectorAll('.color-option').forEach(c => c.classList.remove('active'));
                    colorBtn.classList.add('active');
                    this.selectedColor = shape.color;
                }
            }
        }
    }
    
    deselectAllShapes() {
        this.shapes.forEach(shape => {
            shape.element.classList.remove('selected');
        });
        this.selectedShape = null;
    }
    
    updateShapeColor(shape, color) {
        shape.color = color;
        if (shape.type === 'triangle') {
            shape.element.style.borderBottomColor = color;
        } else {
            shape.element.style.backgroundColor = color;
        }
        this.saveToHistory();
    }
    
    updateShapeSize(shape, size) {
        shape.size = size;
        
        if (shape.type === 'triangle') {
            shape.element.style.borderLeftWidth = (size/2) + 'px';
            shape.element.style.borderRightWidth = (size/2) + 'px';
            shape.element.style.borderBottomWidth = size + 'px';
            shape.element.style.borderBottomColor = shape.color;
        } else if (shape.type === 'rectangle') {
            shape.element.style.width = (size * 1.5) + 'px';
            shape.element.style.height = (size * 0.75) + 'px';
        } else {
            shape.element.style.width = size + 'px';
            shape.element.style.height = size + 'px';
        }
        
        this.saveToHistory();
    }
    
    updateShapeRotation(shape, rotation) {
        shape.rotation = rotation;
        shape.element.style.transform = `rotate(${rotation}deg)`;
        this.saveToHistory();
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
        } else {
            this.showNotification('No shape selected', 'info');
        }
    }
    
    clearCanvas() {
        if (this.shapes.length > 0 && confirm('Clear all shapes?')) {
            this.shapes.forEach(shape => shape.element.remove());
            this.shapes = [];
            this.selectedShape = null;
            this.saveToHistory();
            this.showNotification('Canvas cleared!', 'info');
        }
    }
    
    undo() {
        if (this.shapeHistory.length > 1) {
            this.shapeHistory.pop();
            const previousState = this.shapeHistory[this.shapeHistory.length - 1];
            this.restoreState(previousState);
            this.showNotification('Undo successful!', 'info');
        } else {
            this.showNotification('Nothing to undo', 'info');
        }
    }
    
    saveToHistory() {
        const state = this.shapes.map(shape => ({
            id: shape.id,
            type: shape.type,
            color: shape.color,
            size: shape.size,
            rotation: shape.rotation,
            position: { ...shape.position }
        }));
        this.shapeHistory.push(JSON.parse(JSON.stringify(state)));
        
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
            shape.dataset.type = shapeData.type;
            
            shape.style.left = (shapeData.position.x - shapeData.size/2) + 'px';
            shape.style.top = (shapeData.position.y - shapeData.size/2) + 'px';
            shape.style.transform = `rotate(${shapeData.rotation}deg)`;
            
            if (shapeData.type === 'circle') {
                shape.style.borderRadius = '50%';
                shape.style.backgroundColor = shapeData.color;
                shape.style.width = shapeData.size + 'px';
                shape.style.height = shapeData.size + 'px';
            } else if (shapeData.type === 'triangle') {
                shape.style.width = '0';
                shape.style.height = '0';
                shape.style.backgroundColor = 'transparent';
                shape.style.borderLeft = (shapeData.size/2) + 'px solid transparent';
                shape.style.borderRight = (shapeData.size/2) + 'px solid transparent';
                shape.style.borderBottom = shapeData.size + 'px solid ' + shapeData.color;
            } else if (shapeData.type === 'rectangle') {
                shape.style.backgroundColor = shapeData.color;
                shape.style.width = (shapeData.size * 1.5) + 'px';
                shape.style.height = (shapeData.size * 0.75) + 'px';
            } else {
                shape.style.backgroundColor = shapeData.color;
                shape.style.width = shapeData.size + 'px';
                shape.style.height = shapeData.size + 'px';
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
            const response = await fetch('/api/get_task');
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error('Failed to load task');
            }
            const task = await response.json();
            
            this.currentTask = task;
            this.updateTaskDisplay(task);
            
            // Clear canvas for new task
            this.clearCanvas();
            
            // Hide next button, show done button
            document.getElementById('next-btn').style.display = 'none';
            document.getElementById('done-btn').style.display = 'flex';
            
            this.showNotification(`New task: ${task.name}!`, 'success');
        } catch (error) {
            console.error('Error loading task:', error);
            this.showNotification('Failed to load task', 'error');
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
                size: shape.size + 'px',
                rotation: shape.rotation + 'deg'
            };
        });

        try {
            const response = await fetch('/api/validate_shape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_id: this.currentTask.id,
                    shapes: shapeData
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error('Validation failed');
            }

            const result = await response.json();

            if (result.valid) {
                this.showNotification(
                    `🎉 ${result.message} You earned ${result.award} coins!`,
                    'success'
                );

                // Update coin display
                await this.loadUserStats();

                // Show next button
                document.getElementById('next-btn').style.display = 'flex';
                document.getElementById('done-btn').style.display = 'none';
            } else {
                this.showNotification(`❌ ${result.message} Try again!`, 'error');
            }
        } catch (error) {
            console.error('Validation error:', error);
            this.showNotification('Validation failed', 'error');
        }
    }
    
    async loadUserStats() {
        try {
            const response = await fetch('/api/user_stats');
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error('Failed to load stats');
            }
            const stats = await response.json();
            
            document.getElementById('coin-count').textContent = stats.coins;
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
        }, 3000);
    }
}

// Initialize the game when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ShapeBuilderGame();
});