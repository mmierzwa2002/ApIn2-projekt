from flask import Blueprint, jsonify

errors_bp = Blueprint('errors', __name__)

class ValidationError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = message
        self.status_code = status_code

@errors_bp.app_errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": error.message}), error.status_code

@errors_bp.app_errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": str(error.description)}), 400

@errors_bp.app_errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500