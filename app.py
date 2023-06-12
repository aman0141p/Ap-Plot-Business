import os

import app as app
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
app.use_static_for_assets = True
app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Temporary data to store plots
plots = []

# Temporary data to store users
users = []

# Home page
@app.route('/')
def home():
    return render_template('index.html', plots=plots)


@app.route('/add_plot', methods=['GET', 'POST'])
def add_plot():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Get plot details from the form
        plot_title = request.form['plot_title']
        plot_description = request.form['plot_description']
        plot_contact = request.form['plot_contact']
        plot_location = request.form['plot_location']
        plot_price = request.form['plot_price']

        # Handle the uploaded photo
        plot_photo = request.files['plot_photo']
        if plot_photo:
            filename = secure_filename(plot_photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            plot_photo.save(filepath)
        else:
            filepath = ''

        # Create a new plot with the details
        plot = {
            'title': plot_title,
            'description': plot_description,
            'photo': filename,  # Store the filename instead of the full filepath
            'contact': plot_contact,
            'location': plot_location,
            'price': plot_price,
            'seller': session['username']
        }

        # Add the plot to the plots list
        plots.append(plot)

        return redirect('/')

    return render_template('add_plot.html')




# Edit a plot
@app.route('/edit_plot/<int:plot_id>', methods=['GET', 'POST'])
def edit_plot(plot_id):
    if 'username' not in session:
        return redirect('/login')

    plot = next((p for p in plots if p['id'] == plot_id), None)

    if not plot or plot['seller'] != session['username']:
        return redirect('/')

    if request.method == 'POST':
        # Update plot details from the form
        plot['title'] = request.form['plot_title']
        plot['description'] = request.form['plot_description']
        plot['contact'] = request.form['plot_contact']
        plot['location'] = request.form['plot_location']
        plot['price'] = request.form['plot_price']

        # Handle the uploaded photo
        plot_photo = request.files['plot_photo']
        if plot_photo:
            filename = secure_filename(plot_photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            plot_photo.save(filepath)
            plot['photo'] = filepath

        return redirect('/')

    return render_template('edit_plot.html', plot=plot)



# Delete a plot
@app.route('/delete_plot', methods=['POST'])
def delete_plot():
    if 'plot_id' in request.form:
        plot_id = int(request.form['plot_id'])
        if plot_id < len(plots):
            # Remove the plot from the plots list
            del plots[plot_id]
    return redirect('/')


# Register a user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user details from the form
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        if any(user['username'] == username for user in users):
            return render_template('register.html', error='Username already exists')

        # Create a new user
        user = {
            'username': username,
            'password': generate_password_hash(password)
        }

        # Add user to the temporary data
        users.append(user)

        return redirect('/login')

    return render_template('register.html')


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user details from the form
        username = request.form['username']
        password = request.form['password']

        # Find the user in the temporary data
        user = next((user for user in users if user['username'] == username), None)

        # Check if the user exists and the password is correct
        if user and check_password_hash(user['password'], password):
            # Store the username in the session
            session['username'] = username

            return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


# User logout
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
