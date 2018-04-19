from pprint import pprint
from datetime import datetime

import MySQLdb


def test_user_turnes():
    exfin_connection = MySQLdb.connect(
        host="10.10.100.27",                # host of MySQL database
        user="root",                        # user's username
        passwd="Orraveza(99)",              # your password
        db="mbank",                         # name of the database
        charset="utf8"
    )

    # create CURSOR and set UTF8 params
    exfin_cursor = exfin_connection.cursor()
    exfin_cursor.execute('SET NAMES utf8;')
    exfin_cursor.execute('SET CHARACTER SET utf8;')
    exfin_cursor.execute('SET character_set_connection=utf8;')

    exfin_cursor.execute(
        """
            SELECT 
                id,
                lk_adr_oblast,
                lk_adr_obsh,
                lk_adr_city,
                lk_adr_ul,
                lk_adr_num,
                lk_adr_ap,
                tel_mob_kod,
                tel_mob_num,
                email,
                name,
                name2,
                name3,
                egn
            FROM
                mbank.tpersons
            WHERE id = 144580;
        """
    )
    person_data = exfin_cursor.fetchall()[0]
    print(person_data)

    exfin_cursor.execute(
        """
            SELECT 
                val
            FROM
                mbank.fvalues
            WHERE corrid = {0} and code = 'bdate';
        """.format(person_data[0])
    )
    person_birthday = exfin_cursor.fetchall()[0]

    exfin_cursor.execute(
        """
            SELECT 
                val
            FROM
                mbank.fvalues
            WHERE corrid = {0} and code = 'bplace';
        """.format(person_data[0])
    )
    person_birthday_place = exfin_cursor.fetchall()[0]

    exfin_cursor.execute(
        """
            SELECT 
                name
            FROM
                mbank.tdropdown_details
            WHERE id = {0};
        """.format(person_data[7])
    )
    person_mobile_operator_code = exfin_cursor.fetchall()[0]

    exfin_cursor.execute(
        """
            SELECT name
            from mbank.tdropdown_details
            where dropdown=2 and id = {0}
        """.format(person_data[1])
    )
    person_oblast = exfin_cursor.fetchall()[0]

    exfin_cursor.execute(
        """
            SELECT 
                lists.listname
            FROM
                mbank.fvalues fval
            join 
                (
                    select listname, listcode, listval
                    from mbank.lists
                ) lists on lists.listcode = fval.listcode
                       and lists.listval = fval.val
            WHERE
                corrid = {0}
            and code = 'Street_type_reg';
        """.format(person_data[0])
    )
    person_street_type = exfin_cursor.fetchall()[0]


    exfin_cursor.execute(
        """
            SELECT 
                id, vnoska, suma, egn,
                contract_date, contract_num
            FROM
                mbank.tcredits
            WHERE
                egn = {0};
        """.format(person_data[13])
    )
    person_credits = exfin_cursor.fetchall()
    credits = []
    for credit in person_credits:
        credits.append(
            {
                "pay_step": credit[1],
                "sum": credit[2],
                "contract_date": credit[4].strftime("%d.%m.%Y"),
                "contract_num": credit[5],
            }
        )
    pprint(credits)


    return {
        "names": " ".join([
            person_data[12],
            person_data[10],
            person_data[11]
        ]),
        "address": "{0} обл., {1} район, {2}, {3} {4}, {5}, кв.{6}".format(
            person_oblast[0],
            person_data[2],
            person_data[3],
            person_street_type[0],
            person_data[4],
            person_data[5],
            person_data[6]
        ),
        "email": person_data[9],
        "birthday_place": person_birthday_place[0],
        "birthday": datetime.strptime(person_birthday[0], "%Y-%m-%d").strftime("%d.%m.%Y"),
        "mobile_phone": " ".join([
            person_mobile_operator_code[0],
            person_data[8]
        ]),
        "credits": credits
    }
