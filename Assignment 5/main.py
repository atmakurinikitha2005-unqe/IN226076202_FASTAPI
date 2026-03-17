from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()
# Sample Data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []
order_counter = 1
# Q1 - Search Products
@app.get("/products/search")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(result),
        "products": result
    }
# Q2 - Sort Products
@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }
# Q3 - Pagination
@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit

    paginated = products[start:end]
    total_pages = (len(products) + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": paginated
    }
# Create Orders
@app.post("/orders")
def create_order(customer_name: str):
    global order_counter

    order = {
        "order_id": order_counter,
        "customer_name": customer_name
    }

    orders.append(order)
    order_counter += 1

    return {"message": "Order created", "order": order}
# Q4 - Search Orders
@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not result:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }
# Q5 - Sort by Category then Price
@app.get("/products/sort-by-category")
def sort_by_category():
    sorted_products = sorted(products, key=lambda x: (x["category"], x["price"]))

    return {
        "message": "Sorted by category then price",
        "products": sorted_products
    }
# Q6 - Browse 
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    # Step 1: Filter
    filtered = products
    if keyword:
        filtered = [p for p in filtered if keyword.lower() in p["name"].lower()]

    # Step 2: Sort
    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False
    filtered = sorted(filtered, key=lambda x: x[sort_by], reverse=reverse)

    # Step 3: Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    total_pages = (len(filtered) + limit - 1) // limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": len(filtered),
        "total_pages": total_pages,
        "products": paginated
    }
# BONUS - Orders Pagination
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    paginated = orders[start:end]
    total_pages = (len(orders) + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "orders": paginated
    }
# Product by ID 
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")