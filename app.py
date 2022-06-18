from flask import Flask,jsonify,request,render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
#app.config['FILE_UPLOADS']
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/",methods=['GET'])
def default():
    return render_template('index.html')


@app.route("/upload",methods=['GET','POST'])
def upload():

    if request.method=="POST":

        if request.files:
        # save file
            uploaded_file = request.files['input_csv']
            filename = secure_filename(uploaded_file.filename)
            save_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(save_path)

            df_transactions=pd.read_csv(save_path)

            return render_template("upload.html",
                                    upload_binary=True,
                                   df_transactions=[df_transactions.tail(10).to_html(classes='data',header=True,index=False)])

        else:
            return render_template("upload.html",
                                    failed_upload=True,
                                    upload_binary=False)

    else:
        return render_template('upload.html',
                                upload_binary=False)


@app.route("/transactions",methods=['GET','POST'])
def show_transactions():

    if request.method=="POST":

        # save file
        uploaded_file = request.files['input_csv']
        filename = secure_filename(uploaded_file.filename)
        save_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(save_path)

        df_transactions=pd.read_csv(save_path)

        return render_template("transactions.html",
                               df_transactions=[df_transactions.tail(10).to_html(classes='data',header=True,index=False)])

    else:
        # Check if user already has saved df_transactions
        # if they do then display
        # if not then return to page to upload

        return render_template('index.html')
