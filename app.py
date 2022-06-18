from flask import Flask,jsonify,request,render_template
import pandas as pd
import os
from helper_functions import *
from werkzeug.utils import secure_filename


app = Flask(__name__)
#app.config['FILE_UPLOADS']
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/",methods=['GET','POST'])
def default():

    if request.method=="POST":

        if request.files:
        # save file
            uploaded_file = request.files['input_csv']
            filename = secure_filename(uploaded_file.filename)
            save_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(save_path)

            df_transactions=pd.read_csv(save_path)
            df_transactions=transactions_process(df_transactions)

            dict_data=get_share_summary(df_transactions)
            df_shares=pd.DataFrame.from_dict(dict_data['individual_tickers'],orient='index')

            col_rename={'code_avg_buy_price':'Avg buy price',
                'code_amount':'Number of shares',
                'money_change_code':'Profit (£)',
                'pct_code':'Percentage change (%)',
                'code_in':'Cash invested',
                'code_value':'Value of shares',
                'code_latest_price':'Latest Price',
                'ticker':'Stock'}

            numerical_cols=['Number of shares',
            'Avg buy price',
            'Latest Price',
            'Value of shares',
            'Profit (£)',
            'Percentage change (%)']

            df_shares=df_shares.rename(columns=col_rename)
            df_shares=df_shares[['Stock']+numerical_cols].copy()

            return render_template("index.html",
                                    upload_binary=True,
                                    df_transactions=[df_transactions[['Date','Ticker','Action','Number','Price','Total']].tail(10).to_html(classes='data',header=True,index=False)],
                                    df_shares=[df_shares.to_html(classes='data',header=True,index=False)])

        else:
            return render_template("index.html",
                                    failed_upload=True,
                                    upload_binary=False)

    else:
        return render_template('index.html',
                                upload_binary=False)
