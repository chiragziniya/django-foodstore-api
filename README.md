# Django Menu & Inventory API

Backend assignment for menu and inventory management system using Django REST Framework.

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create virtual environment
```bash
python -m venv .venv
```

### 3. Activate virtual environment
**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Database Configuration

**For Local Development (SQLite - Recommended):**
- The project uses SQLite by default for local development
- No additional configuration needed
- Just ensure `.env` file has `DIRECT_URL` commented out or removed

**For Production Server (PostgreSQL):**
- Create a `.env` file in the project root
- Add your PostgreSQL connection string:
```env
DIRECT_URL=postgresql://username:password@host:port/database
```

Example `.env` for local development:
```env
# Keep DIRECT_URL commented for SQLite (local development)
# DIRECT_URL=postgresql://user:pass@localhost:5432/mydb
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Seed the database (optional but recommended)
```bash
python manage.py seed_data
```

This creates 2 stores with 11 menu items and inventory covering all test scenarios:
- Almost gone items (quantity <= 5)
- Out of stock items (quantity = 0)
- Inactive items
- Normal stock items

The seeder will display all created IDs and ready-to-use API testing commands.

### 8. Run the development server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### 1. List Store Menu
```
GET /stores/{store_id}/menu/
```
Returns all menu items for a specific store with availability and stock status.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Veg Burger",
    "price": "129.00",
    "quantity": 3,
    "is_available": true,
    "almost_gone": true
  }
]
```

### 2. Update Inventory
```
PATCH /inventory/{menu_item_id}/
```
Updates the inventory quantity for a menu item.

**Request:**
```json
{
  "quantity": 10
}
```

**Response:**
```json
{
  "quantity": 10,
  "is_available": true,
  "almost_gone": false
}
```

### 3. Place Order
```
POST /orders/
```
Places an order and deducts inventory atomically.

**Request:**
```json
{
  "store_id": 1,
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2
    }
  ]
}
```

**Response:**
```json
{
  "message": "Order placed successfully"
}
```

## Running Tests

```bash
python manage.py test
```

## Business Rules

- `ALMOST_GONE_THRESHOLD = 5`
- A menu item is **available** if it's active and has quantity > 0
- A menu item is **almost gone** if quantity > 0 and quantity <= 5
- Orders are validated before processing
- All inventory updates are atomic

## Tech Stack

- Django 5.2.11
- Django REST Framework 3.16.1
- SQLite (Local Development)
- PostgreSQL (Production - Optional)
- Python-dotenv for environment configuration