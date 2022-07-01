from time import timezone
from unicodedata import category
from django.dispatch import receiver
from django.shortcuts import redirect, render
from core.forms import*
from django.contrib import messages
from core.models import*
from django.utils import timezone
from django.shortcuts import*
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
from twilio.rest import Client

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET))
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


# Create your views here.
def index(request):
    products = Product.objects.all()
    if not(products):
        messages.info(request, 'No Items Added Yet!')

    return render(request, 'core/index.html', {'products':products})


def search(request):
    title_search = request.GET['title']
    products = Product.objects.filter(name__icontains=title_search) 
    if not(products):
        messages.info(request, 'No Items Found!')

    return render(request, 'core/search.html', {'products':products})


def add_item(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            print('True')
            instance = form.save(commit=False)
            name = Customer.objects.get(user=request.user)
            instance.poster = name
            instance.save()
            print('Data Saved Successfully')
            messages.info(request, 'Item Added Sucessfully!')
            return redirect('add_item')
        else:
            print(form.errors)
            messages.info(request, 'Item Not Added. Try Again!')
        
    else:
        form = ProductForm()
    return render (request, 'core/add_item.html', {'form':form})


def item_description(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'core/item_description.html', {'product':product})


def item_image(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'core/item_image.html', {'product':product})


def add_to_cart(request, pk):
    # Get the particular product of id = pk
    product = Product.objects.get(pk=pk)

    # Create order item
    order_item, created = OrderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )


    # Get Query Set of Ordered Object of Particular User
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            messages.info(request, "Item Already Added to Cart!")
            return redirect("item_description", pk=pk)

        else:
            order.items.add(order_item)
            messages.info(request, "Successfully Added to Cart!")
            return redirect("item_description", pk=pk)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Successfully Added to Cart!")
        return redirect("item_description", pk=pk)



def order_list(request):
    if Order.objects.filter(user=request.user, ordered=False).exists():
        order = Order.objects.get(user=request.user, ordered=False)
        return render(request, 'core/order_list.html', {'order' : order})
        
    return render(request, 'core/order_list.html', {'message' : 'Cart is Empty!'})



def remove_from_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False,
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item = OrderItem.objects.filter(
                product = item,
                user = request.user,
                ordered = False
            )[0]
            
            order_item.delete()
            messages.info(request, "")
            return redirect("order_list")

        else:
            messages.info(request, "")
            return redirect("order_list")

    else:
        messages.info(request, "No Orders Found!")
        return redirect("order_list")



def checkout_page(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        messages.info(request, 'Address Already Registered!')
        return render(request, 'core/checkout.html', {'payment_allow':'allow'})
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        try:
            if form.is_valid():
                address = form.cleaned_data.get('address')
                city = form.cleaned_data.get('city')
                zip_code = form.cleaned_data.get('zip_code')

                checkout_address = CheckoutAddress(
                    user = request.user,
                    address = address,
                    city = city,
                    zip_code = zip_code,
                )

                checkout_address.save()
                messages.info(request, 'Address Added Sucessfully!')
                return render(request, 'core/checkout.html', {'payment_allow':'allow'})

        except Exception as e:
            messages.warning(request, "Checkout Failed!")
            return redirect('checkout')

    else:
        form = CheckoutForm()
        return render(request, 'core/checkout.html', {'form' : form})


    
def payment(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        final_address = CheckoutAddress.objects.get(user=request.user)
        order_amount = order.get_grand_total()
        order_currency = "INR"
        order_receipt = order.order_id
        notes = {
            "address" : final_address.address,
            "city" : final_address.city,
            "zip_code" : final_address.zip_code,
        }
        razorpay_order = razorpay_client.order.create(
            dict(
                amount = order_amount * 100,
                currency = order_currency,
                receipt = order_receipt,
                notes = notes,
                payment_capture = "0",
            )
        )
        print(razorpay_order["id"])
        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        return render(
            request,
            "core/paymentsummary.html",
            {
                "order" : order,
                "order_id" : razorpay_order["id"],
                "orderId" : order.order_id,
                "final_price" : order_amount,
                "razorpay_merchant_id" : settings.RAZORPAY_ID,
            },
        )

    except Order.DoesNotExist:
        print("Order Not Found!")
        return HttpResponse("404 Error")



@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get("razorpay_payment_id", "")
            order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            print(payment_id, order_id, signature)

            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
                print("Order Found!")
            except:
                print("Order Not Found!")
                return HttpResponse("505 Not Found")

            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            print("Working!")
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            
            if result is not None:
                print("Working Final Fine!")
                amount = order_db.get_grand_total()
                amount = amount * 100
                payment_status = razorpay_client.payment.capture(payment_id, amount)

                if payment_status is not None:
                    print(payment_status)
                    order_db.ordered = True
                    order_db.save()
                    print("Payment Success!")
                    checkout_address = CheckoutAddress.objects.get(user=request.user)
                    request.session[
                        "order_complete"
                    ] = "Order Placed Successfully! Expect Delivery Within 14-20 Working Days!"
                    
                    orderitem_db = OrderItem.objects.get(user=request.user)
                    product_name = orderitem_db.get_product()
                    product_db = Product.objects.get(name=product_name)
                    product_db.available = False
                    product_db.save()

                    try:

                        print("Twilio Working!")
                        
                        orderitem_db = OrderItem.objects.get(user=request.user)
                        item_price = orderitem_db.get_final_price()
                        product_name = orderitem_db.get_product()

                        product_db = Product.objects.get(name=product_name)
                        item_name = product_db.get_product_name()
                        poster_phone = product_db.get_poster_phone()
                        poster_phone = "+91" + poster_phone
                        poster_name = product_db.get_poster_name()

                        order_db = Order.objects.get(razorpay_order_id=order_id)
                        buyer_name = order_db.get_user()

                        sms = f"Congratulations {poster_name}! Your item '{item_name}' has been ordered by {buyer_name}. Nexscrap Team will pick up the item from the provided address within 7-10 working days and pay you ₹{item_price} at time of pickup. Regards from Nexscrap Pvt. Ltd!"
                        
                        message = twilio_client.messages.create(
                            body = sms,
                            from_ = settings.TWILIO_PHONE_NO,
                            to = poster_phone,
                        )
                        print("Message Sent!")
                        print(message.sid)

                    except:
                        pass

                    return render(request, "invoice/invoice.html", {"order" : order_db, "payment_status" : payment_status, "checkout_address" : checkout_address})

                
                else:
                    print("Payment Failed!")
                    order_db.ordered = False
                    order_db.save()
                    request.session[
                        "order_failed"
                    ] = "Order Failed! Please Try Again!"
                    return redirect("/")

            else:
                order_db.ordered = False
                order_db.save()
                return render(request, "core/paymentfailed.html")

        except:
            return HttpResponse("Error Occured")


def invoice(request):
    return render(request, "invoice/invoice.html")

