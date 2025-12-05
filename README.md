# FastAPI Example

A simple FastAPI example application demonstrating authentication, REST API endpoints, and data validation.

## Features

- **JWT Authentication**: Secure endpoints with JSON Web Token authentication
- **RESTful API**: Clean API design with CRUD operations
- **Food Generator**: Random food name generator with adjectives
- **Items Management**: Create, read, and update items with validation
- **Pydantic Models**: Data validation using Pydantic

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/xiao-e-yun/Fastapi_example.git
cd Fastapi_example
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the server with:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Public Endpoints

- `GET /` - Hello World endpoint
- `POST /login` - Login with username and password to get JWT token
- `GET /items/` - List items
- `GET /items/{id}` - Get item by ID
- `POST /items/` - Create new item
- `PUT /items/{id}` - Update item by ID

### Protected Endpoints (Requires Authentication)

- `GET /foods/{id}` - Get a random food name by ID
- `GET /foods/` - List random food names

### Authentication

To access protected endpoints:

1. Login to get a token:
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

2. Use the token in subsequent requests:
```bash
curl -X GET "http://localhost:8000/foods/1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Environment Variables

- `JWT_SECRET_TOKEN`: Secret key for JWT token signing (optional, auto-generated if not set)

## Project Structure

```
.
├── main.py           # Main application file with API endpoints
├── auth.py           # Authentication and JWT handling
├── requirements.txt  # Python dependencies
├── food.txt          # List of food names
├── adjectives.txt    # List of adjectives for food names
└── README.md         # This file
```

## Development

### Adding New Dependencies

After adding new packages, update the requirements file:
```bash
pip freeze > requirements.txt
```

### Running in Production

For production deployment, set the `JWT_SECRET_TOKEN` environment variable:
```bash
export JWT_SECRET_TOKEN="your-secret-key-here"
uvicorn main:app --host 0.0.0.0 --port 8000
```

## License

This is an example project for educational purposes.
