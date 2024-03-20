from website.forms import RegisterForm, LoginForm, ProductFilterForm,OrderTimeForm,PaymentForm
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from website.models import Vehicle, User, db, Order, Temporary_order, Payment
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta
import random
import json
import re
from sqlalchemy import and_


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:    
            user_to_create= User(first_name= form.first_name.data, surname=form.surname.data, email_address= form.email_address.data, password= form.password1.data , gender=str(form.gender.data), phone_code=str(form.phone_code.data), phone_number=form.phone_number.data,birth=form.birth.data, driver_license=form.driver_license.data, id_passport=form.id_passport.data, category=str(form.category.data))
            db.session.add(user_to_create)
            db.session.commit() 
            print(user_to_create)
            login_user(user_to_create)
            flash(f"Account created successfully! You are now logged in as {user_to_create.first_name}", category="success")
            return redirect(url_for('views.home_page'))
        
        except IntegrityError:
            flash('ID passport or Driver license already exists! Please try a different one.', category='danger')
            return render_template('register_page.html', form=form)
    
    if form.errors != {}: 
        for err_msg in form.errors.values():
            if err_msg == ['Email address already exists! Please try a different email address']:
                flash('Email address already exists! Please try a different email address', category='danger')  
            elif err_msg == ['Not a valid date value.']:
                flash('Invlid birth date! Please try a different date', category="danger")
            elif err_msg == ['Field must be equal to password1.']:
                flash('Password confirmation is not correct', category='danger')
            elif err_msg == ['Invalid email address.']:
                flash('Invalid email address.', category='danger')
            print(err_msg)

    return render_template('register_page.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user= User.query.filter_by(email_address=form.email.data).first()
        
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.first_name} {attempted_user.surname}', category='success')
            return redirect(url_for('views.home_page'))
        else:
            if attempted_user ==None:
                flash('Username is not Correct! Please try another one', category= 'danger')
            elif attempted_user.check_password_correction(attempted_password=form.password.data) == False:
                flash('Password is incorrect! Please try another one', category= 'danger')

    else:
        print(form.errors)

    return render_template('login_page.html', form=form)


@auth.route("/logout", methods=['POST','GET'])
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('views.home_page'))

@auth.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    product_filter=ProductFilterForm()
    
    if request.method == 'GET':
        cart=Order.query.filter_by(owner_id=current_user.id, state="Live").all()

        brand_filter = request.args.get('brand')
        doors_filter = request.args.get('doors')
        type_filter = request.args.get('type')
        passengers_filter = request.args.get('passengers')
        daily_filter = request.args.get('daily_price')
        AC_filter = request.args.get('AC')
        fuel_filter= request.args.get('fuel')
        baggage_filter= request.args.get('baggage')

        one_year_ago = datetime.now().date() - timedelta(days=365)

        vehicles = Vehicle.query.filter(and_(Vehicle.owner_id.is_(None), Vehicle.inspection > one_year_ago, Vehicle. next_review > date.today()))        
        def filter_by_brand(vehicles, brand_filter):
            if brand_filter and brand_filter != 'Select brand':
                return vehicles.filter_by(item_name=brand_filter)
            return vehicles

        def filter_by_doors(vehicles, doors_filter):
            if doors_filter and doors_filter != 'Select number of doors':
                return vehicles.filter_by(doors=doors_filter)
            return vehicles

        def filter_by_type(vehicles, type_filter):
            if type_filter and type_filter != 'Select type':
                return vehicles.filter_by(item_type=type_filter)
            return vehicles

        def filter_by_passengers(vehicles, passengers_filter):
            if passengers_filter and passengers_filter != 'Select number of passengers':
                return vehicles.filter_by(passengers=passengers_filter)
            return vehicles
        
        def filter_by_dailyprice(vehicles, daily_filter):
            if daily_filter and daily_filter != 'Select daily price':
                return vehicles.filter_by(daily_price=daily_filter)
            return vehicles
        
        def filter_by_AC(vehicles, AC_filter):
            if AC_filter and AC_filter != 'Need AC?':
                return vehicles.filter_by(AC=AC_filter)
            return vehicles
        
        def filter_by_fuel(vehicles, fuel_filter):
            if fuel_filter and fuel_filter != 'Select brand':
                return vehicles.filter_by(fuel=fuel_filter)
            return vehicles
        
        def filter_by_baggage(vehicles, baggage_filter):
            if baggage_filter and baggage_filter != 'Need baggage?':
                return vehicles.filter_by(baggage=baggage_filter)
            return vehicles
        
        if brand_filter != 'Select brand':
            vehicles = filter_by_brand(vehicles, brand_filter)
        
        if doors_filter != 'Select category':
            vehicles = filter_by_doors(vehicles, doors_filter)
        
        if type_filter != 'Select type':

            vehicles = filter_by_type(vehicles, type_filter)
        
        if passengers_filter != 'Select passengers':
            vehicles = filter_by_passengers(vehicles, passengers_filter)


        if daily_filter != 'Select daily price':
            vehicles = filter_by_dailyprice(vehicles, daily_filter)

        if AC_filter != 'Need AC?':
            vehicles = filter_by_AC(vehicles, AC_filter)

        if fuel_filter != 'Select fuel':
            vehicles = filter_by_fuel(vehicles, fuel_filter)
        
        if baggage_filter != 'Need baggage?':
            vehicles = filter_by_baggage(vehicles, baggage_filter)

        vehicles = vehicles.all()

    return render_template('market_page.html', cart=cart, brand_filter=brand_filter, vehicles=vehicles, product_filter=product_filter)

@auth.route('/reset_filter', methods=['GET'])
def reset_filter():
    # Logic for resetting the filter
    # Redirect back to original page
    return redirect(url_for('auth.market_page'))

@auth.route("/product_page/<int:vehicle_id>", methods=['POST', 'GET'])
@login_required

def product_page(vehicle_id):
    ordertimeform= OrderTimeForm()
    
    if request.method =='POST':
        days=0
        cart = session.get('cart', [])
        category_budget_limit = int(re.search(r'\((\d+)\$', current_user.category).group(1))
        vehicle = Vehicle.query.filter_by(id=vehicle_id ).first()
        if vehicle:
            if vehicle.item_price > category_budget_limit:
                print(vehicle.item_price)
                flash('This vehicle exceeds your budget limit.', category='danger')
                return render_template('product_page.html', ordertimeform=ordertimeform, vehicle=vehicle)
            vehicle_dict = vehicle.to_dict()
            json_data = json.dumps(vehicle_dict)
            
            check_in_datetime=None
            days=0
            check_out_datetime=None

            if ordertimeform.validate_on_submit():
                check_in = ordertimeform.start.data
                check_out = ordertimeform.finish.data

                if check_in >= date.today() and check_out >= date.today() and check_out > check_in:
                        #Convert dates to datetime objects
                    check_in_datetime = datetime.combine(check_in, datetime.min.time())
                    check_out_datetime = datetime.combine(check_out, datetime.min.time())
                    is_vehicle_repeated = Vehicle.query.filter_by(owner_id = None).first()
                    temp_order_repreated= Temporary_order.query.filter_by(product_id=vehicle.id).first()

                    if is_vehicle_repeated:    
                        #Calculate the difference in days
                        days = (check_out_datetime - check_in_datetime).days
                        is_temp_order=Temporary_order.query.filter_by(product_id=vehicle.id, owner_id=current_user.id).first()
                        existing_order = Order.query.filter_by(product_id=vehicle.id, owner_id=current_user.id, state="Live").first()
                        new_price=0
                        if days == 0:
                            flash('Please select a longer renting time!')

                        elif is_temp_order:
                            flash('You already choose this vehicle. Please try another one!', category='danger')

                        elif existing_order:
                            old_price= existing_order.order_price
                            temp_order = Temporary_order(
                                    product_id=vehicle.id,
                                    days=days,
                                    owner_id=current_user.id,
                                    start=check_in_datetime,
                                    finish=check_out_datetime,
                                    daily_price=vehicle.daily_price,
                                    order_price=vehicle.daily_price * days,
                                    price_exchange= new_price - old_price
                                )
                            
                            new_price= temp_order.order_price
                            
                            if is_temp_order is not None:
                                db.session.delete(is_temp_order)
                                db.session.commit()
                            db.session.add(temp_order)
                            
                            db.session.commit()
                            print(temp_order.to_dict())
                            
                            
                            flash('Your rent details have been updated. Please review the changes!', category='success')
                            return render_template('product_page.html', temp_order=temp_order, ordertimeform=ordertimeform, vehicle=vehicle, check_in_datetime=check_in_datetime, check_out_datetime=check_out_datetime)
                        else:
                            temp_order = Temporary_order(
                                    product_id=vehicle.id,
                                    days=days,
                                    owner_id=current_user.id,
                                    start=check_in_datetime,
                                    finish=check_out_datetime,
                                    daily_price=vehicle.daily_price,
                                    order_price=vehicle.daily_price * days
                                )
                            
                            if is_temp_order is not None:
                                db.session.delete(is_temp_order)
                                db.session.commit()
                            db.session.add(temp_order)
                            
                            db.session.commit()
                            print(temp_order.to_dict())
                            
                            
                            flash('This vehicle was added to your cart. Congratulations!', category='success')
                            return render_template('product_page.html',temp_order=temp_order, ordertimeform=ordertimeform, vehicle=vehicle, check_in_datetime=check_in_datetime, check_out_datetime=check_out_datetime)
                    else:
                        flash('This vehicle is unavailable. Please try another one!', category='danger')
                        return render_template('product_page.html',temp_order=temp_order, ordertimeform=ordertimeform, vehicle=vehicle, check_in_datetime=check_in_datetime, check_out_datetime=check_out_datetime)
                        
                else:
                    flash("We can't guarantee this dates. Please try again!", category='danger')
                    
            else:
                flash('Your renting time is not defined! Please try again', category='danger')
            return render_template('product_page.html', ordertimeform=ordertimeform, vehicle=vehicle)
        
    if request.method =='GET':
        cart=Order.query.filter_by(owner_id=current_user.id, state="Live").all()
        days=0
        vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
        related_filter= Vehicle.query.filter_by(item_price=vehicle.item_price, item_type=vehicle.item_type).all()
        related_products=random.sample(related_filter, min(5, len(related_filter))) # select until 5 random products with same price 
        check_in=ordertimeform.start.data
        check_out=ordertimeform.finish.data
        return render_template('product_page.html', vehicle_id=vehicle_id, cart=cart, days=days, ordertimeform=ordertimeform, vehicle=vehicle, related_products=related_products)


@auth.route("/cart_page", methods=['GET', 'POST'])
@login_required

def purchase():
    payment_form = PaymentForm()
    if request.method == 'POST':
        if 'order_id_to_delete' in request.form:
            order_id_to_delete = request.form.get('order_id_to_delete')

            if order_id_to_delete:
                order_to_delete = Temporary_order.query.get(order_id_to_delete)

                if order_to_delete:
                    db.session.delete(order_to_delete)
                    db.session.commit()
                    flash('Order successfully deleted.', category='success')

                else:
                    flash('Order not found.', category='danger')

            return redirect(url_for('auth.purchase'))
        
        if 'purchase' in request.form:
            temp_orders = Temporary_order.query.filter_by(owner_id=current_user.id).all()

            if not temp_orders:
                flash('Please add some vehicles to your cart and try again!', category='danger')
                return redirect(url_for('auth.purchase'))
            
            for temp_order in temp_orders:
                vehicle_ordered = Vehicle.query.filter_by(id=temp_order.product_id).first()

                if vehicle_ordered:
                    existing_order = Order.query.filter_by(product_id=vehicle_ordered.id, owner_id=current_user.id, state="Live").first()
                    if existing_order:
                        
                        
                        #Update existing order
                        existing_order.product_id = temp_order.product_id
                        existing_order.days = temp_order.days
                        existing_order.start = temp_order.start
                        existing_order.finish = temp_order.finish
                        existing_order.daily_price = temp_order.daily_price
                        existing_order.order_price = temp_order.order_price

                        payment= Payment(amount= session.get('final_price_order'), card_type=request.form.get('paymentMethod'), id_user=current_user.id, id_order=existing_order.id)
                        if payment.card_type == "":
                                
                            flash('Please select a card type!', category='danger')
                            return redirect(url_for('auth.purchase'))
                        else:
                            db.session.add(payment)
                            flash('Your rent was exchanged. Please confirm all the details', category='success')
                    else:
                        #Create new order
                        if temp_order.finish.date() > date.today() and temp_order.start.date() >= date.today():
                            new_order = Order(
                                product_id=temp_order.product_id,
                                owner_id=current_user.id,
                                days=temp_order.days,
                                start=temp_order.start,
                                finish=temp_order.finish,
                                daily_price=temp_order.daily_price,
                                order_price=temp_order.order_price,
                                state= "Live"
                            )
                            db.session.add(new_order)
                            db.session.commit()
                            
                            payment= Payment(amount= session.get('final_price_order'), card_type=str(request.form.get('paymentMethod')), id_user=current_user.id, id_order=new_order.id)

                            if payment.card_type == "":
                                flash('Please select a card type!', category='danger')
                                return redirect(url_for('auth.purchase'))
                            else:
                                db.session.add(payment)
                                flash('Your rent are done. Have a nice ride!', category='success')
                        #Remove temporary order
                    db.session.delete(temp_order)
                
                #Update vehicle owner_id
                vehicle_ordered.owner_id = current_user.id
            
            #Commit changes
            db.session.commit()
            
            return redirect(url_for('views.home_page'))
        else:
            flash('These vehicles are no longer available. Try different ones!', category='danger')
            return redirect(url_for('auth.purchase'))

    if request.method == 'GET':
        cart = Order.query.filter_by(owner_id=current_user.id, state="Live").all()
        temp_orders = Temporary_order.query.filter_by(owner_id=current_user.id).all()
        
        if not temp_orders:
            vehicles_nr = 0
            final_price_order = 0
            final_price_vehicle = 0
            return render_template('cart_page.html', payment_form=payment_form,cart=cart, final_price_order=final_price_order, final_price_vehicle=final_price_vehicle, vehicles_nr=vehicles_nr)

        final_price_order = 0
        temp_orders_list = []

        for temp_order in temp_orders:
            vehicle = Vehicle.query.filter_by(id=temp_order.product_id).first()
            existing_order = Order.query.filter_by(product_id=temp_order.product_id, owner_id=current_user.id, state="Live").first()
            
            if existing_order:
                #Calculate the price exchange if there is an existing order
                price_exchange = temp_order.order_price - existing_order.order_price
                final_price_order += price_exchange
                if final_price_order < 0:
                    flash('The price exchange will be refunded to you.', category='info')
            else:
                #For new orders, simply add the order price
                final_price_order += temp_order.order_price
            
            if vehicle:
                temp_orders_list.append({
                    'temp_order': temp_order,
                    'vehicle': vehicle
                })
        session['final_price_order'] = final_price_order
        vehicles_nr = len(temp_orders_list)  #Number of vehicles in cart
        final_price_vehicle = sum(temp_order['temp_order'].daily_price * temp_order['temp_order'].days for temp_order in temp_orders_list)

        return render_template('cart_page.html', cart=cart,temp_orders=temp_orders, final_price_order=final_price_order, temp_orders_list=temp_orders_list, final_price_vehicle=final_price_vehicle, vehicles_nr=vehicles_nr)
    
@auth.route('/cart-management', methods=['GET','POST'])
@login_required
def order_management():
    if request.method == 'POST':
        if 'order_id_to_delete' in request.form:
            order_id_to_delete = request.form.get('order_id_to_delete')
            print(f"Attempting to delete order ID: {order_id_to_delete}")

            if order_id_to_delete:
                order_to_delete = Order.query.filter_by(id=order_id_to_delete).first()
                if order_to_delete:
                    vehicle= Vehicle.query.filter_by(id= order_to_delete.product_id).first()
                    db.session.delete(order_to_delete)
                    vehicle.owner_id= None
                    db.session.commit()
                    flash('Cancelation completed!', category='success')
                    return redirect(url_for('auth.order_management'))

                else:
                    flash('Order not found.', category='danger')
            return redirect(url_for('auth.market_page'))
        
        if 'check_out' in request.form:
            check_out = request.form.get('check_out')
            if check_out:
                order_to_check_out=Order.query.filter_by(id=check_out).first()

                if order_to_check_out:
                    vehicle =Vehicle.query.filter_by(id= order_to_check_out.product_id).first()
                    vehicle.owner_id= None
                    order_to_check_out.state="Finished"
                    db.session.commit()
                    flash('Check out successfull. Thank you for your choice!', category='success')
                    return redirect(url_for('views.home_page'))
                
                else:
                    flash('Order not found.', category='danger')
                           
    elif request.method == 'GET':
        orders= Order.query.filter_by(owner_id=current_user.id, state="Live").all()
        orders_list=[]
        for order in orders:
                vehicle=Vehicle.query.filter_by(id=order.product_id).first()

                if vehicle:
                    orders_list.append({
                        'order':order,
                        'vehicle': vehicle
                    })

                if order.finish.date() < date.today() :
                    order.state = "Finished"
                    vehicle.owner_id=None
        
        try: 
            return render_template('cart_management_page.html', orders_list=orders_list, vehicle=vehicle)
        except:
            return render_template('home_page.html')





