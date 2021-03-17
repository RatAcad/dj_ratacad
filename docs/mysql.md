## Get Account to RatAcad Datajoint-MySQL database

The RatAcad MySQL database is managed by IS&T. Please follow the instructions below to get a personal account to access the database.

1. Email IS&T (ithelp@bu.edu) to create your account and give you permissions. Please include the information below. Bob Given (bgiven@bu.edu) from IS&T usually responds to these tickets in < 24 hr, sending secure mail with a temporary password. For now, you can bug Gary to take care of this step.
    - database url: buaws-aws-cf-rds-mysql-prod.cenrervr4svx.us-east-2.rds.amazonaws.com
    - your bu username
    - you want access from BU-VPN, BU-802.1X, and BU ethernet ip addresses
    - permission to read from the following databases: "scott_rat", "scott_bpod", "scott_flashes"

2. Log on to the MySQL server and change your password:
    - install mysql client on your computer
      - windows: [instructions here](https://dev.mysql.com/doc/mysql-shell/8.0/en/mysql-shell-install-windows-quick.html) (this is untested)
      - mac using [homebrew](https://brew.sh/): `brew install mysql-client`
      - ubuntu: `apt install mysql-client`
    - log in to the MySQL server
      - run in terminal: `mysql -h buaws-aws-cf-rds-mysql-prod.cenrervr4svx.us-east-2.rds.amazonaws.com -u <your_user_name> -p`
      - type in your temporary password and hit enter
    - Change your password to `MyNewPass`
      - run: `ALTER USER '<your_user_name>'@'168.122.%' IDENTIFIED BY 'MyNewPass'`

3. Continue setting up Rat Academy Datajoint: see [Getting Started](setup.md)

