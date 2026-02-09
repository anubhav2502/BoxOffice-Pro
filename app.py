from flask import Flask, render_template
from db import init_app

app = Flask(__name__)
app.config['SECRET_KEY'] = "This_is_a_secrete_key"
init_app(app)

#REgister buleprint
from auth.routes import auth_bp
from admin.routes import admin_bp
from customer.routes import customer_bp
from tech_admin.routes import tech_admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(tech_admin_bp, url_prefix='/tech_admin')

# root Route (landing page)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)


