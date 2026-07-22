from flask import Blueprint, render_template, session, redirect, request, jsonify, flash
from utils.history import get_prediction_history, get_prediction_count, delete_prediction, clear_prediction_history
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

history = Blueprint("history", __name__, url_prefix="/history")


@history.route("/")
def view_history():
    """View prediction history with pagination"""
    if "admin" not in session:
        return redirect("/")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    records = get_prediction_history(limit=per_page, offset=(page - 1) * per_page)
    total_count = get_prediction_count()
    
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    return render_template(
        "history.html",
        records=records,
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )


@history.route("/delete/<int:prediction_id>", methods=["POST"])
def delete_prediction_route(prediction_id):
    """Delete a prediction from history"""
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if delete_prediction(prediction_id):
        return jsonify({"success": True})
    return jsonify({"error": "Failed to delete"}), 500


@history.route("/clear", methods=["POST"])
def clear_history():
    """Clear all prediction history"""
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if clear_prediction_history():
        flash("All prediction history cleared!", "info")
        return jsonify({"success": True})
    return jsonify({"error": "Failed to clear"}), 500