from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()
products = [
    {
        "id": 1,
        "name": "Wireless Mouse",
        "price": 499,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 2,
        "name": "Notebook",
        "price": 99,
        "category": "Stationery",
        "in_stock": True
    },
    {
        "id": 3,
        "name": "USB Hub",
        "price": 800,
        "category": "Electronics",
        "in_stock": False
    },
    {
        "id": 4,
        "name": "Pen Set",
        "price": 49,
        "category": "Stationery",
        "in_stock": True
    }
]

feedback = []
orders = []
# Q1 — FILTER PRODUCTS USING QUERY PARAMETERS
@app.get("/products/filter")
def filter_products(
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    category: Optional[str] = None
):
    filtered = products

    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]

    if category is not None:
        filtered = [
            p for p in filtered
            if p["category"].lower() == category.lower()
        ]

    return filtered
# Q2 — GET ONLY PRODUCT NAME AND PRICE
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}
# Q3 — CUSTOMER FEEDBACK USING PYDANTIC
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }
# Q4 — PRODUCT SUMMARY DASHBOARD
@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    out_stock_products = [p for p in products if not p["in_stock"]]

    most_expensive_product = max(products, key=lambda p: p["price"])
    cheapest_product = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock_products),
        "out_of_stock_count": len(out_stock_products),
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        },
        "cheapest": {
            "name": cheapest_product["name"],
            "price": cheapest_product["price"]
        },
        "categories": categories
    }
# Q5 — BULK ORDER VALIDATION
class OrderItem(BaseModel):

    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):

    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next(
            (p for p in products if p["id"] == item.product_id),
            None
        )

        if product is None:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }
#  BONUS — ORDER STATUS TRACKINGs
class Order(BaseModel):

    customer_name: str
    product_id: int
    quantity: int


@app.post("/orders")
def create_order(order: Order):

    order_id = len(orders) + 1

    new_order = {
        "order_id": order_id,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order


@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}