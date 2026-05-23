from app import create_app, db

app = create_app()

@app.route('/')
def index():
    return """
    <h1>System Praktyk</h1>
    <a href='/auth/login/microsoft'>Zaloguj przez Microsoft</a><br>
    <a href='/auth/login/google'>Zaloguj przez Google</a>
    """

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        
    app.run(debug=True, port=5000)