from flask import Flask, request, jsonify
from datetime import datetime
from models.leave import Leave
from models.user import User
from db import app, db


with app.app_context():
    db.create_all()

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    if 'username' not in data or 'password' not in data or 'role' not in data:
        return jsonify({'error': 'Invalid input data'}), 400

    new_user = User(username=data['username'], password=data['password'], role=data['role'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/leave', methods=['POST'])
def create_leave():
    data = request.get_json()

    if data.get('start_date') is None or data.get('end_date') is None or data.get('reason') is None:
        return jsonify({'error': 'Invalid input data'}), 400

    new_leave = Leave(
        user_id=1,  # Replace with the actual user_id
        start_date=data['start_date'],
        end_date=data['end_date'],
        reason=data['reason'],
        status='pending'
    )

    db.session.add(new_leave)
    db.session.commit()

    return jsonify({'message': 'Leave created successfully'}), 201

@app.route('/leave/<leave_id>', methods=['DELETE'])
def delete_leave(leave_id):
    leave = Leave.query.get(leave_id)
    if not leave:
        return jsonify({'error': 'Leave schedule not found'}), 404

    db.session.delete(leave)
    db.session.commit()

    return jsonify({'message': 'Leave schedule deleted successfully'}), 200

@app.route('/leave/daysleft', methods=['GET'])
def get_days_left():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Invalid user id'}), 400
    
    today = datetime.now()
    leaves = Leave.query.filter_by(user_id=user_id).filter(Leave.end_date > today).all()
    days_left = sum([(leave.end_date - today).days + 1 for leave in leaves])

    return jsonify({'days_left': days_left}), 200

@app.route('/leave/admin', methods=['GET'])
def get_all_leaves():
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        return jsonify({'error': 'No admin user found'}), 404

    leaves = Leave.query.filter(Leave.status != 'approved').all()
    result = [
        {
            'leave_id': leave.id,
            'user_id': leave.user_id,
            'start_date': leave.start_date.strftime('%Y-%m-%d'),
            'end_date': leave.end_date.strftime('%Y-%m-%d'),
            'reason': leave.reason,
            'status': leave.status
        }
        for leave in leaves
    ]

    return jsonify({'leaves': result}), 200


if __name__ == "__main__":
    app.run(debug=True)

