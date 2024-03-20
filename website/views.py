from flask import Blueprint, render_template,request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from website.models import Order, db
from datetime import datetime, date



views = Blueprint('views', __name__)
@views.route('/', methods=['GET', 'POST'])

def home_page():


    if request.method =='GET':

        if current_user.is_authenticated:
            cart=Order.query.filter_by(owner_id=current_user.id, state="Live").all()
            #refresh the live orders just to be sure that all orders are finished after check out time. Maybe not so correct, but I didn't find a solution to turn this site automatic
            orders= Order.query.filter_by(owner_id=current_user.id, state="Live").all()
            if orders:
                for order in orders:
                    if order.finish.date() < date.today():
                        order.vehicle.owner_id= None
                        order.state="Finished"
                        db.session.commit()
            return render_template('home_page.html', cart=cart)
        else:

            return render_template('home_page.html')
    
    
