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
                tcr.id,
                tcr.vnoska,
                tcr.suma,
                tcr.egn,
                tcr.contract_date,
                tcr.contract_num,

                pays_calendar.number_of_pays,
                pays_calendar.full_sum,
                pays_calendar.already_paid,
                pays_calendar.rest_pays_sum,
                pays_calendar.number_of_rest_pays,
                pays_calendar.last_pay_date,
                tst.status
            FROM
                mbank.tcredits tcr
            left join(
                SELECT 
                    tpp_main.id,
                    tpp_main.credit_id,
                    count(*) as number_of_pays,
                    sum(tpp_main.sum) as full_sum,
                    ifnull(tpp_join.already_paid, 0) as already_paid,
                    sum(tpp_main.sum) - ifnull(tpp_join.already_paid, 0) as rest_pays_sum,
                    count(*) - tpp_join.paid_pays as number_of_rest_pays,
                    date(max(tpp_main.data)) as last_pay_date
                FROM
                    mbank.tpp tpp_main
                LEFT join 
                (   
                    select id, sum(sum) as already_paid, count(*) as paid_pays
                    from mbank.tpp
                    where ispaid = 1
                    group by credit_id
                ) tpp_join on tpp_join.id = tpp_main.id
                group by tpp_main.credit_id
            ) pays_calendar on pays_calendar.credit_id = tcr.id

            join mbank.tstatuses tst on tst.credit_id = tcr.id and tst.status = 5 and tst.credit_id not in (
                select tst11.credit_id from mbank.tstatuses tst11 
                where tst11.status in (11, 111)
            )
            WHERE
                tcr.egn = {0} and tcr.is_otpusnat = 1;
        """.format(person_data[13])
    )
    person_credits = exfin_cursor.fetchall()

    credits = []
    for credit in person_credits:
        exfin_cursor.execute(
            """
                SELECT max(dt) last_date, dolg_all, crd_id
                from dwh.credits_saldo
                where crd_id = {0}
                group by crd_id
            """.format(credit[0])
        )
        credit_dolg = exfin_cursor.fetchall()

        exfin_cursor.execute(
            """
                SELECT
                    id,
                    credit_id,
                    sum,
                    data,
                    ispaid
                from mbank.tpp
                where credit_id = {0}
            """.format(credit[0])
        )
        credit_tpp = exfin_cursor.fetchall()


        tpp_data_list = []
        pay_sums = []
        dolg_sums = []
        rest_sums = []
        for i, tpp in enumerate(credit_tpp):
            try:
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'in' 
                          and nomenclature = 4 
                          and iscredit = {0} 
                          and date(vreme) between '{1}' and '{2}'
                        group by iscredit
                    """.format(credit[0], tpp[3], credit_tpp[i+1][3])
                )
            except Exception:
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'in' 
                          and nomenclature = 4 
                          and iscredit = {0} 
                          and date(vreme) > '{1}'
                        group by iscredit
                    """.format(credit[0], tpp[3])
                )
            tcash_in_sum = exfin_cursor.fetchall()


            try:
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'out' 
                          and nomenclature = 7
                          and iscredit = {0} 
                          and date(vreme) between '{1}' and '{2}'
                        group by iscredit
                    """.format(credit[0], tpp[3], credit_tpp[i+1][3])
                )
            except Exception:
                exfin_cursor.execute(
                    """
                        SELECT sum(sum) as how_paid, iscredit, vreme
                        from mbank.tcash
                        where type = 'out' 
                          and nomenclature = 7
                          and iscredit = {0} 
                          and date(vreme) > '{1}'
                        group by iscredit
                    """.format(credit[0], tpp[3])
                )
            tcash_dolg_sum = exfin_cursor.fetchall()

            # print(tcash_dolg_sum)

            pay_sum = tcash_in_sum[0][0] if tcash_in_sum else 0
            pay_sums.append(pay_sum)
            dolg_sum = tcash_dolg_sum[0][0] if tcash_dolg_sum else 0
            dolg_sums.append(dolg_sum)

            rest_sum = credit[7] - sum(dolg_sums) - sum(pay_sums)
            rest_sums.append(rest_sum)

            tpp_data_list.append(
                {
                    "data": tpp[3],
                    "pay_sum": pay_sum,
                    "dolg_sum": dolg_sum,
                    "ispaid": tpp[4],
                    "sum_must_pay": float(tpp[2]) - float(dolg_sum),
                    "rest_sum": rest_sums[i-1] if i > 0 else credit[7] - dolg_sum
                }
            )




        credits.append(
            {
                "pay_step": credit[1],
                "sum": credit[2],
                "contract_date": credit[4].strftime("%d.%m.%Y"),
                "contract_num": credit[5],
                "number_of_pays": credit[6],
                "full_sum": credit[7],
                "already_paid": credit[8],
                "rest_pays_sum": credit[9],
                "number_of_rest_pays": credit[10],
                "last_pay_date": credit[11].strftime("%d.%m.%Y"),
                "dolg": credit_dolg[0][1],
                "pay_step_with_dolg": credit[1] + credit_dolg[0][1],
                "tpp": tpp_data_list
            }
        )
    # pprint(credits)

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
