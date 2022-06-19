# stock-investment-manager
A Flask app to manage portfolio of stocks

- Upload your transactions log. An example is provided in the sample directory

- The share must be available on Yahoo Finance at this address:
'https://finance.yahoo.com/quote/'+ share + '/key-statistics?p=' + share

- Run the web-app by cloning the repository and running `flask run` from the command line.

- For more information see here: https://flask.palletsprojects.com/en/2.1.x/quickstart/

- Upload your file.

- Process transactions will calculate  how many shares you have remaining after the buying and selling, the average buy price, the latest price (scraped from Yahoo Finance), the value of your shares, 
the profit (in $), and the percentage change.
