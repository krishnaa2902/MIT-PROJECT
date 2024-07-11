from flask import Blueprint, render_template, flash, request, jsonify, render_template_string
from flask_login import login_required, current_user
from .models import Note, Item, Pattern
from . import db
import json
from bs4 import BeautifulSoup
import requests
import re
from flask_talisman import Talisman
from website import create_app

pattern_library = []


views = Blueprint('views', __name__)

# this is the homepage


@views.route('/', methods=['GET', 'POST'], endpoint='home')
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('note is too short', category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('note has been created', category="success")
    return render_template('home.html', user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})


def find_malicious_patterns(input_text):
    # script_pattern = r'<script.*?>.*?<\/script>'
    pattern_list = Pattern.query.all()
    print("pattern list")
    print(pattern_list)
    for i in pattern_list:
        print(i.patternName)
        matched_pattern = re.findall(i.patternName, input_text)
        if matched_pattern:
            return matched_pattern
    return None


# def update_pattern_library(malicious_patterns):
#     global pattern_library
#     pattern_library.extend(malicious_patterns)
#     print('Updating pattern library with malicious patterns:', malicious_patterns)


@views.route('/catalog', methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        cat = request.form.get('search')

        malicious_patterns = find_malicious_patterns(cat)

        if malicious_patterns:
            flash("malicious script detected - { " + " ".join(malicious_patterns) + " }", category="error")
            item_list = Item.query.all()
        else:
            # if malicious_patterns:
            #     # Update the dynamic pattern library with the discovered malicious patterns
            #     update_pattern_library(malicious_patterns)

            item_list = Item.query.filter_by(category=cat).all()
            print(f"itemlist  == = {item_list}")
            if item_list == []:
                flash('no items found', category="error")
                item_list = Item.query.all()
            else:
                flash('items found', category="success")

    else:
        item_list = Item.query.all()
        # for item in item_list:
        #     print(f"{item.name} {item.category} {item.description} {item.price}")
        cat = request.args.get('category')
        item_list = Item.query.filter_by(category=cat).all()
        # print(f"itemlist  == = {item_list}")
        if item_list == []:
            if cat:
                flash('no items found', category="error")
            item_list = Item.query.all()
        else:
            flash('items found', category="success")
    return render_template('catalog.html', user=current_user, item_list=item_list, category=cat)


@views.route('/seller', methods=['GET', 'POST'])
def seller():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('desc')
        price = request.form.get('price')

        # print(f"name = {name}")
        # print(f"category = {category}")
        # print(f"description = {description}")
        # print(f"price = {price}")

        new_item = Item(name=name, category=category, description=description, price=price)
        db.session.add(new_item)
        db.session.commit()

    return render_template('seller.html', user=current_user)


@views.route('/delete-product', methods=['POST'])
def delete_product():
    item = json.loads(request.data)
    itemId = item['itemId']
    item = Item.query.get(itemId)
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({})


@views.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        user_input = request.form.get('input')
        return render_template_string('<p>' + user_input + '</p>')
    return '''
    <form method="POST">
        <input type="text" name="input">
        <input type="submit" value="Submit">
    </form>
    '''


def create_pattern_to_match_all(arr):
    # Escape special characters and join keywords with the positive lookahead assertion (?=)
    escaped_keywords = [re.escape(keyword) for keyword in arr]
    pattern_string = "(?=.*" + ")(?=.*".join(escaped_keywords) + ")"
    pattern = f"^{pattern_string}.*$"
    return pattern


@views.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return render_template('admin.html', user=current_user)

    if request.method == 'POST':
        global pattern_library
        user_input = request.form.get('pattern')
        arr = user_input.split(' ')
        new_pattern = Pattern(patternName=create_pattern_to_match_all(arr))
        db.session.add(new_pattern)
        db.session.commit()
        pattern_library += [create_pattern_to_match_all(arr)]
    return render_template('admin.html', user=current_user)


@views.route('/csp-report', methods=['POST'])
def csp_report():
    report_data = request.get_json()
    # Handle and log the CSP violation report
    print(f"REPORT DATA FROM CSP {report_data}")
    return 'CSP violations have been reported', 200


@views.route('/dom', methods=['GET', 'POST'])
def dom():
    response = requests.get('http://localhost:5000/catalog')
    soup = BeautifulSoup(response.content, 'html.parser')

    # print(str(soup))
    pattern1 = r'<img[^>]*\s+onerror\s*=\s*".*?"[^>]*>'
    pattern2 = r'<script(?![^>]*\s+src\s*=\s*"(?:https://cdn\.jsdelivr\.net/npm/bootstrap@5\.3\.2/dist/js/bootstrap\.bundle\.min\.js|/static/index\.js)")[^>]*>.*?</script>'
    list_of_scripts1 = re.findall(pattern1, str(soup))
    list_of_scripts2 = re.findall(pattern2, str(soup))

    # print(list_of_scripts1)
    # print(list_of_scripts2)
    pattern_library = []
    pattern_list = Pattern.query.all()
    for i in pattern_list:
        pattern_library.append(i.patternName)

    list_of_scripts_12 = list_of_scripts1 + list_of_scripts2
    return {"list_of_scripts in catalog": list_of_scripts_12,
            "catalog": [str(soup)],
            "pattern_library": pattern_library}
