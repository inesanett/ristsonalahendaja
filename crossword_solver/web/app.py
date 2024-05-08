import os
import sys
from flask import Flask, render_template, request, Blueprint
from werkzeug.utils import secure_filename
from collections import defaultdict
from crossword_solver.solver_utils import find_whole_crossword_candidates
from crossword_solver.crossword_solver import solve_crossword
from crossword_solver.crossword_detection import detect_crossword_from_file
from visualisations import plot_square_types, plot_solution_texts

site = Blueprint("ristsona", __name__, template_folder = "templates", static_folder = "static")
UPLOAD_FOLDER = os.path.join(site.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

CROSSWORDS = dict()
ALL_CROSSWORD_SOLUTIONS = defaultdict(list)
# Crossword name : [(image, score, intersections), (image, score, intersections)]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@site.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('index.html', description="Lae üles pildifail ristsõnast.\nSobivad vormingud: png, jpeg, jpg.")

    # check if the post request has the file part
    if 'filename' not in request.files:
        return render_template('index.html', description="Fail on tühi")
    file = request.files['filename']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return render_template('index.html', description="Unustasid faili valida")
    if file and not allowed_file(file.filename):
        return render_template('index.html', description="See faili formaat ei ole toetatud")
    
    # For saving file
    filename = secure_filename(file.filename)
    local_file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(local_file_path)

    # Detect crossword
    crossword = detect_crossword_from_file(local_file_path)
    CROSSWORDS[filename] = crossword
    ALL_CROSSWORD_SOLUTIONS[filename] = []

    base64img = plot_square_types(crossword)

    # delete file
    #os.remove(os.path.join(UPLOAD_FOLDER, filename))

    return render_template('detected_crossword.html', base64img=base64img, crossword_name=filename)


@site.route("/solved_crossword/<string:crossword_name>/<int:id>")
def solved_crossword(crossword_name, id):
    crossword = CROSSWORDS[crossword_name]
    if len(ALL_CROSSWORD_SOLUTIONS[crossword_name])==0:
        # Solve crossword
        find_whole_crossword_candidates(CROSSWORDS[crossword_name])
        results = solve_crossword(crossword)
        
        topn_results = sorted(results, key=lambda x: x[2], reverse = True)[:10]
        topn_results = [(plot_solution_texts(crossword, matrix), round(score), intersections) for matrix, score, intersections in topn_results]
        ALL_CROSSWORD_SOLUTIONS[crossword_name] = topn_results
    
    return render_template("solved_crossword.html",
                           crossword_name = crossword_name,
                           solution_id = id, 
                           solutions = ALL_CROSSWORD_SOLUTIONS[crossword_name], 
                           base64img = ALL_CROSSWORD_SOLUTIONS[crossword_name][id][0])


if __name__ == "__main__":
    app = Flask(__name__)
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    if len(sys.argv)>1:
        app.register_blueprint(site, url_prefix=sys.argv[1])
    else:
        app.register_blueprint(site)
    
    app.run(debug=True, host="0.0.0.0", threaded=False)
