from database import Database
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def save_prediction(prediction_type, input_data, result):
    """Save a prediction to the database"""
    try:
        with Database() as db:
            db.execute_query(
                """INSERT INTO prediction_history (prediction_type, input_data, result) 
                   VALUES (%s, %s, %s)""",
                (prediction_type, input_data, str(result))
            )
            return True
    except Exception as e:
        print(f"Error saving prediction: {e}")
        return False


def get_prediction_history(limit=20, offset=0):
    """Get prediction history with pagination"""
    try:
        with Database() as db:
            records = db.fetch_all(
                """SELECT id, prediction_type, input_data, result, created_at 
                   FROM prediction_history 
                   ORDER BY created_at DESC 
                   LIMIT %s OFFSET %s""",
                (limit, offset)
            )
            return records if records else []
    except Exception as e:
        print(f"Error getting prediction history: {e}")
        return []


def get_prediction_count():
    """Get total number of predictions"""
    try:
        with Database() as db:
            result = db.fetch_one("SELECT COUNT(*) as count FROM prediction_history")
            return result['count'] if result else 0
    except Exception as e:
        print(f"Error getting prediction count: {e}")
        return 0


def delete_prediction(prediction_id):
    """Delete a prediction by ID"""
    try:
        with Database() as db:
            db.execute_query(
                "DELETE FROM prediction_history WHERE id = %s",
                (prediction_id,)
            )
            return True
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return False


def clear_prediction_history():
    """Clear all prediction history"""
    try:
        with Database() as db:
            db.execute_query("DELETE FROM prediction_history")
            return True
    except Exception as e:
        print(f"Error clearing prediction history: {e}")
        return False


def get_recent_predictions(limit=5):
    """Get recent predictions for dashboard"""
    return get_prediction_history(limit=limit, offset=0)


def get_latest_prediction():
    """Get the most recent prediction"""
    try:
        with Database() as db:
            record = db.fetch_one(
                """SELECT id, prediction_type, input_data, result, created_at 
                   FROM prediction_history 
                   ORDER BY created_at DESC 
                   LIMIT 1"""
            )
            return record
    except Exception as e:
        print(f"Error getting latest prediction: {e}")
        return None