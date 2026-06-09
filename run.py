from app import create_app, db

app = create_app()

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)