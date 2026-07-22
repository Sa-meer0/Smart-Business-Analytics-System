from flask import Blueprint, render_template, request, redirect, session, flash
from database import Database
import sys
import os

# Add parent directory to path for database import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():
    """Login page with session persistence"""
    
    # If already logged in, redirect to dashboard
    if session.get("admin"):
        return redirect("/dashboard")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password", "warning")
            return render_template("login.html")

        with Database() as db:
            admin = db.fetch_one(
                "SELECT * FROM admin WHERE username = %s",
                (username,)
            )

        if admin and admin["password"] == password:
            # Set session with permanent flag for persistence
            session["admin"] = username
            session.permanent = True
            flash(f"Welcome back, {username}!", "success")
            return redirect("/dashboard")

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@auth.route("/logout")
def logout():
    """Logout and clear session"""
    session.clear()
    flash("You have been logged out", "info")
    return redirect("/")