import razorpay

client = razorpay.Client(auth=("rzp_test_2Ye6LH82OehWTV", "JG9uyYXj1gaLYsfKxG8hCaBQ"))

def create_payment_order(amount_in_rupees, receipt_id):
    order = client.order.create({
        "amount": amount_in_rupees * 100,
        "currency": "INR",
        "receipt": receipt_id,
        "payment_capture": 1
    })
    return order
