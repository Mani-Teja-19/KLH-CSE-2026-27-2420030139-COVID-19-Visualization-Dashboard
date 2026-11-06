from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=========================================================")
    print("COVID-19 Visualization Dashboard Web Application")
    print("Serving at: http://127.0.0.1:5000")
    print("Default Credentials:")
    print("  - Admin:   admin  / admin123")
    print("  - Doctor:  doctor / doctor123")
    print("  - Staff:   staff  / staff123")
    print("=========================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
