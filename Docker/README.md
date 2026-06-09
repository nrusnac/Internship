# Docker Learning Project

All tasks completed successfully!

## What's Inside

### Task 1: Jupyter Notebook Server
- Dockerfile with Python 3.11, Jupyter, and data science libraries
- Mounted local Git repository for file access
- Port 8888 exposed for browser access
- Can install packages via pip inside the container

### Task 2: PostgreSQL Database Container
- Official PostgreSQL 15 image
- Schema with `departments` and `employees` tables (linked by foreign key)
- `predictions` table for storing ML model results
- Auto-initialized with sample data via `init.sql`

### Task 3: Train and Save ML Model
- Jupyter notebook that trains Random Forest classifier on Iris dataset
- Achieves ~96% accuracy on test set
- Model serialized with joblib to `/workspace/Docker/models/iris_model.joblib`
- Can be loaded and used for predictions

### Task 4: Flask Prediction Service
- Flask API that loads trained model at startup
- `/predict` endpoint accepts flower measurements (JSON) and returns species prediction with confidence scores
- `/history` endpoint retrieves stored predictions from database
- Saves all predictions to PostgreSQL `predictions` table
- Runs on port 5001

### Task 5: Docker Compose Orchestration
- Single `docker-compose.yml` defines all three services
- Custom `internship-network` for inter-container communication
- Health checks ensure database is ready before Flask starts
- Volume mounting for code and data persistence
- Environment variables for database credentials